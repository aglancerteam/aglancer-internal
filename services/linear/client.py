"""
Linear API client: create issues, comments, and update issue description.
Uses GraphQL API at https://api.linear.app/graphql with LINEAR_API_KEY.
"""
import os
import httpx

LINEAR_API_URL = os.getenv("LINEAR_API_URL", "https://api.linear.app/graphql")


def _headers():
    key = os.getenv("LINEAR_API_KEY")
    if not key:
        return None
    return {
        "Authorization": key,
        "Content-Type": "application/json",
    }


def _post(query: str, variables: dict) -> tuple[dict | None, str | None]:
    """Returns (data, error_message). data is None on failure; error_message is set when Linear returns errors."""
    h = _headers()
    if not h:
        return None, "LINEAR_API_KEY is not set"
    try:
        r = httpx.post(
            LINEAR_API_URL,
            json={"query": query, "variables": variables},
            headers=h,
            timeout=15,
        )
        r.raise_for_status()
        body = r.json()
        if body.get("errors"):
            errs = body["errors"]
            msg = errs[0].get("message", str(errs)) if errs else "Unknown Linear API error"
            return None, msg
        return body.get("data"), None
    except httpx.HTTPStatusError as e:
        return None, f"HTTP {e.response.status_code}"
    except Exception as e:
        return None, str(e)


def get_teams() -> tuple[list[dict], str | None]:
    """Return (teams, error). teams is list of { id, name }; error is set on failure."""
    data, err = _post("query { teams(first: 20) { nodes { id name } } }", {})
    if err:
        return [], err
    if not data:
        return [], "No data from Linear"
    nodes = data.get("teams", {}).get("nodes", [])
    return nodes, None


def get_workflow_states(team_id: str) -> tuple[list[dict], str | None]:
    """Return (states, error). states is list of { id, name }. Uses team.states to avoid filter format issues."""
    data, err = _post(
        """query($teamId: String!) {
          team(id: $teamId) {
            states {
              nodes { id name }
            }
          }
        }""",
        {"teamId": team_id},
    )
    if err:
        return [], err
    if not data or not data.get("team"):
        return [], "No data from Linear or team not found"
    nodes = data.get("team", {}).get("states", {}).get("nodes", [])
    return nodes, None


def create_issue(team_id: str, title: str, state_id: str | None = None) -> tuple[dict | None, str | None]:
    """
    Create a Linear issue. Returns (issue_dict, error). issue_dict is { id, identifier, title }; error is set on failure.
    """
    input_vars: dict = {"teamId": team_id, "title": title}
    if state_id:
        input_vars["stateId"] = state_id
    data, err = _post(
        """mutation CreateIssue($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue { id identifier title }
          }
        }""",
        {"input": input_vars},
    )
    if err:
        return None, err
    if not data:
        return None, "No data from Linear"
    payload = data.get("issueCreate")
    if payload and payload.get("success") and payload.get("issue"):
        return payload["issue"], None
    return None, "issueCreate did not return success"


def create_comment(issue_id: str, body: str) -> dict | None:
    """
    Post a comment on a Linear issue. issue_id is the Linear issue UUID/id.
    Returns the comment payload or None on failure.
    """
    h = _headers()
    if not h:
        return None
    mutation = """
    mutation CreateComment($input: CommentCreateInput!) {
      commentCreate(input: $input) {
        success
        comment { id body }
      }
    }
    """
    variables = {"input": {"issueId": issue_id, "body": body}}
    try:
        r = httpx.post(
            LINEAR_API_URL,
            json={"query": mutation, "variables": variables},
            headers=h,
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("errors"):
            print(f"Linear commentCreate errors: {data.get('errors')}")
            return None
        payload = data.get("data", {}).get("commentCreate")
        if payload and payload.get("success"):
            return payload
        return None
    except Exception:
        return None


def get_issue(issue_id: str) -> tuple[dict | None, str | None]:
    """Return (issue_dict, error). issue_dict has id, team_id, state { id, name }."""
    data, err = _post(
        """query($id: String!) {
          issue(id: $id) {
            id
            team { id }
            state { id name }
          }
        }""",
        {"id": issue_id},
    )
    if err:
        return None, err
    if not data or not data.get("issue"):
        return None, "Issue not found"
    issue = data["issue"]
    team = issue.get("team") or {}
    state = issue.get("state") or {}
    return {
        "id": issue["id"],
        "team_id": team.get("id"),
        "state": {"id": state.get("id"), "name": state.get("name")},
    }, None


def update_issue_state(issue_id: str, state_id: str) -> bool:
    """Update a Linear issue's state. Returns True if successful."""
    data, err = _post(
        """mutation UpdateIssueState($id: String!, $input: IssueUpdateInput!) {
          issueUpdate(id: $id, input: $input) {
            success
            issue { id state { id name } }
          }
        }""",
        {"id": issue_id, "input": {"stateId": state_id}},
    )
    if err:
        return False
    if not data:
        return False
    payload = data.get("issueUpdate")
    return bool(payload and payload.get("success"))


def set_issue_state_by_name(issue_id: str, state_name: str) -> tuple[bool, str | None]:
    """
    Set an issue's state by state name (e.g. 'Ready for Spec'). Resolves team and workflow states.
    Returns (success, error_message).
    """
    issue, err = get_issue(issue_id)
    if err or not issue:
        return False, err or "Could not fetch issue"
    team_id = issue.get("team_id")
    if not team_id:
        return False, "Issue has no team"
    states, err = get_workflow_states(team_id)
    if err or not states:
        return False, err or "Could not fetch workflow states"
    state_id = None
    for s in states:
        if (s.get("name") or "").strip().lower() == state_name.strip().lower():
            state_id = s.get("id")
            break
    if not state_id:
        return False, f"State '{state_name}' not found in team workflow"
    ok = update_issue_state(issue_id, state_id)
    return ok, None if ok else "issueUpdate failed"


def update_issue_description(issue_id: str, description: str) -> bool:
    """
    Update a Linear issue's description. issue_id is the Linear issue UUID/id.
    Returns True if successful.
    """
    h = _headers()
    if not h:
        return False
    mutation = """
    mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
        issue { id description }
      }
    }
    """
    variables = {"id": issue_id, "input": {"description": description}}
    try:
        r = httpx.post(
            LINEAR_API_URL,
            json={"query": mutation, "variables": variables},
            headers=h,
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("errors"):
            print(f"Linear issueUpdate errors: {data.get('errors')}")
            return False
        payload = data.get("data", {}).get("issueUpdate")
        return bool(payload and payload.get("success"))
    except Exception:
        return False
