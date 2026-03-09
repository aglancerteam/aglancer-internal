import { useState, useEffect } from "react";

const SwrlyBrandPage = () => {
  const [activeTab, setActiveTab] = useState("identity");
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setTimeout(() => setVisible(true), 100);
  }, []);

  const colors = {
    midnight: "#0D0F1C",
    deep: "#141729",
    surface: "#1C1F3A",
    accent: "#7B6FF0",
    accentLight: "#A599FF",
    accentGlow: "rgba(123, 111, 240, 0.15)",
    teal: "#3ECFB4",
    tealGlow: "rgba(62, 207, 180, 0.15)",
    coral: "#FF6B8A",
    text: "#E8E6F0",
    textMuted: "#8A87A8",
    textDim: "#5C5980",
  };

  const taglines = [
    { text: "Orchestrate AI agents that actually work together.", type: "Primary" },
    { text: "Build agent teams. Ship workflows. Move fast.", type: "Developer-focused" },
    { text: "Your agents, your rules, your integrations.", type: "Control-focused" },
    { text: "From solo agent to full swirl.", type: "Playful" },
  ];

  const voiceExamples = [
    { context: "Homepage hero", copy: "Stop babysitting AI agents. Start orchestrating them." },
    { context: "Feature section", copy: "Connect Claude Code agents to Linear, Slack, and anything with an API. Templates get you started. Custom logic makes it yours." },
    { context: "CTA button", copy: "Start building free" },
    { context: "Pricing page", copy: "Pay for what your agents run, not how many seats you fill." },
    { context: "Social post", copy: "Just shipped: agent templates for sprint planning, code review, and bug triage. Plug in your Linear API key and go." },
    { context: "Error state", copy: "Something got tangled. We're untangling it now." },
  ];

  const visualIdentity = [
    { label: "Logo Concept", desc: "The word 'swrly' in a custom lowercase logotype with a subtle spiral integrated into the 'w' or 'y'. Clean, geometric, but with one organic curve that feels alive." },
    { label: "Primary Colors", desc: "Deep midnight navy (#0D0F1C) as the base, electric purple (#7B6FF0) as the primary accent, and teal (#3ECFB4) as the secondary. This palette feels technical but approachable." },
    { label: "Typography", desc: "Display: A geometric sans-serif with character (like Satoshi, General Sans, or Cabinet Grotesk). Body: A clean, highly readable sans (like Plus Jakarta Sans or DM Sans)." },
    { label: "Iconography", desc: "Custom line icons with rounded caps and a consistent 1.5px stroke. Occasional use of flowing/curved lines to echo the 'swirl' motif without being literal." },
    { label: "Motion Language", desc: "Smooth, flowing transitions. Elements enter with gentle curves rather than straight lines. Loading states use a subtle orbital animation. The brand should feel like things are always gracefully in motion." },
    { label: "Illustration Style", desc: "Abstract node-and-flow diagrams showing agents connecting. Not robotic — more like constellations or neural pathways. Gradients from purple to teal on dark backgrounds." },
  ];

  const namingSystem = [
    { element: "Agent", term: "Agent", note: "Keep it standard — developers know this term" },
    { element: "Group of agents", term: "Swirl", note: "Your branded term. 'Create a new swirl' feels natural" },
    { element: "Workflow template", term: "Template", note: "Don't over-brand utility features" },
    { element: "Integration", term: "Connector", note: "Linear connector, Slack connector" },
    { element: "Agent execution", term: "Run", note: "Standard, maps to billing ('runs/month')" },
    { element: "Workspace", term: "Space", note: "Clean, simple. 'Your spaces'" },
  ];

  return (
    <div style={{
      minHeight: "100vh",
      background: `linear-gradient(180deg, ${colors.midnight} 0%, ${colors.deep} 50%, ${colors.midnight} 100%)`,
      color: colors.text,
      fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
      overflow: "hidden",
    }}>
      {/* Ambient background glow */}
      <div style={{
        position: "fixed", top: "-20%", right: "-10%", width: "600px", height: "600px",
        background: `radial-gradient(circle, ${colors.accentGlow} 0%, transparent 70%)`,
        borderRadius: "50%", pointerEvents: "none", zIndex: 0,
      }} />
      <div style={{
        position: "fixed", bottom: "-15%", left: "-5%", width: "500px", height: "500px",
        background: `radial-gradient(circle, ${colors.tealGlow} 0%, transparent 70%)`,
        borderRadius: "50%", pointerEvents: "none", zIndex: 0,
      }} />

      <div style={{ position: "relative", zIndex: 1, maxWidth: "900px", margin: "0 auto", padding: "40px 24px" }}>
        {/* Header */}
        <div style={{
          opacity: visible ? 1 : 0, transform: visible ? "translateY(0)" : "translateY(20px)",
          transition: "all 0.8s cubic-bezier(0.16, 1, 0.3, 1)",
          marginBottom: "48px",
        }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: "12px", marginBottom: "8px" }}>
            <span style={{
              fontSize: "48px", fontWeight: 800, letterSpacing: "-2px",
              background: `linear-gradient(135deg, ${colors.accent} 0%, ${colors.teal} 100%)`,
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            }}>swrly</span>
            <span style={{ fontSize: "14px", color: colors.textDim, fontWeight: 500, letterSpacing: "2px", textTransform: "uppercase" }}>Brand Kit</span>
          </div>
          <p style={{ color: colors.textMuted, fontSize: "17px", lineHeight: 1.6, maxWidth: "600px" }}>
            Everything you need to launch a consistent, memorable brand for your AI agent orchestration platform.
          </p>
        </div>

        {/* Tab Navigation */}
        <div style={{
          display: "flex", gap: "4px", marginBottom: "36px", padding: "4px",
          background: colors.surface, borderRadius: "12px", width: "fit-content",
        }}>
          {[
            { id: "identity", label: "Visual Identity" },
            { id: "voice", label: "Brand Voice" },
            { id: "naming", label: "Product Naming" },
            { id: "launch", label: "Launch Copy" },
          ].map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              padding: "10px 20px", borderRadius: "8px", border: "none", cursor: "pointer",
              fontSize: "14px", fontWeight: 600, fontFamily: "inherit",
              background: activeTab === tab.id ? colors.accent : "transparent",
              color: activeTab === tab.id ? "#fff" : colors.textMuted,
              transition: "all 0.2s ease",
            }}>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Visual Identity Tab */}
        {activeTab === "identity" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* Color Palette */}
            <div style={{
              background: colors.surface, borderRadius: "16px", padding: "28px",
              border: `1px solid rgba(123, 111, 240, 0.1)`,
            }}>
              <h3 style={{ fontSize: "13px", textTransform: "uppercase", letterSpacing: "2px", color: colors.textDim, marginBottom: "20px", fontWeight: 600 }}>Color Palette</h3>
              <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                {[
                  { name: "Midnight", hex: "#0D0F1C", light: false },
                  { name: "Deep", hex: "#141729", light: false },
                  { name: "Surface", hex: "#1C1F3A", light: false },
                  { name: "Accent", hex: "#7B6FF0", light: false },
                  { name: "Teal", hex: "#3ECFB4", light: false },
                  { name: "Coral", hex: "#FF6B8A", light: false },
                ].map(c => (
                  <div key={c.name} style={{ textAlign: "center" }}>
                    <div style={{
                      width: "72px", height: "72px", borderRadius: "12px", background: c.hex,
                      border: `1px solid rgba(255,255,255,0.08)`, marginBottom: "8px",
                      boxShadow: c.name === "Accent" ? `0 4px 20px ${colors.accentGlow}` : "none",
                    }} />
                    <div style={{ fontSize: "12px", fontWeight: 600, color: colors.text }}>{c.name}</div>
                    <div style={{ fontSize: "11px", color: colors.textDim, fontFamily: "monospace" }}>{c.hex}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Identity Elements */}
            {visualIdentity.map((item, i) => (
              <div key={i} style={{
                background: colors.surface, borderRadius: "16px", padding: "24px",
                border: `1px solid rgba(123, 111, 240, 0.1)`,
              }}>
                <div style={{
                  fontSize: "11px", textTransform: "uppercase", letterSpacing: "2px",
                  color: colors.accent, fontWeight: 700, marginBottom: "8px",
                }}>{item.label}</div>
                <p style={{ color: colors.text, fontSize: "15px", lineHeight: 1.7, margin: 0 }}>{item.desc}</p>
              </div>
            ))}
          </div>
        )}

        {/* Brand Voice Tab */}
        {activeTab === "voice" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div style={{
              background: colors.surface, borderRadius: "16px", padding: "28px",
              border: `1px solid rgba(123, 111, 240, 0.1)`,
            }}>
              <h3 style={{ fontSize: "13px", textTransform: "uppercase", letterSpacing: "2px", color: colors.textDim, marginBottom: "16px", fontWeight: 600 }}>Voice Principles</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                {[
                  { trait: "Direct, not corporate", desc: "Say 'Build agent teams' not 'Leverage our multi-agent orchestration capabilities.'" },
                  { trait: "Technical, not jargon-heavy", desc: "Your audience knows what APIs and webhooks are. Don't explain basics, but don't gatekeep with obscure terminology either." },
                  { trait: "Confident, not arrogant", desc: "Show what the product does. Let the work speak. Skip superlatives like 'revolutionary' and 'game-changing.'" },
                  { trait: "Playful where it fits", desc: "Error messages, empty states, and social media can have personality. Docs and pricing should be clear and straight." },
                ].map((v, i) => (
                  <div key={i} style={{ paddingLeft: "16px", borderLeft: `2px solid ${colors.accent}` }}>
                    <div style={{ fontWeight: 700, color: colors.text, fontSize: "15px", marginBottom: "4px" }}>{v.trait}</div>
                    <div style={{ color: colors.textMuted, fontSize: "14px", lineHeight: 1.6 }}>{v.desc}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Taglines */}
            <div style={{
              background: colors.surface, borderRadius: "16px", padding: "28px",
              border: `1px solid rgba(123, 111, 240, 0.1)`,
            }}>
              <h3 style={{ fontSize: "13px", textTransform: "uppercase", letterSpacing: "2px", color: colors.textDim, marginBottom: "20px", fontWeight: 600 }}>Tagline Options</h3>
              {taglines.map((t, i) => (
                <div key={i} style={{
                  padding: "16px", marginBottom: i < taglines.length - 1 ? "12px" : 0,
                  background: colors.deep, borderRadius: "10px",
                  border: `1px solid rgba(123, 111, 240, 0.06)`,
                }}>
                  <span style={{
                    fontSize: "10px", textTransform: "uppercase", letterSpacing: "1.5px",
                    color: colors.teal, fontWeight: 700,
                  }}>{t.type}</span>
                  <div style={{ fontSize: "18px", fontWeight: 700, color: colors.text, marginTop: "6px" }}>{t.text}</div>
                </div>
              ))}
            </div>

            {/* Copy Examples */}
            <div style={{
              background: colors.surface, borderRadius: "16px", padding: "28px",
              border: `1px solid rgba(123, 111, 240, 0.1)`,
            }}>
              <h3 style={{ fontSize: "13px", textTransform: "uppercase", letterSpacing: "2px", color: colors.textDim, marginBottom: "20px", fontWeight: 600 }}>Copy Examples</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {voiceExamples.map((ex, i) => (
                  <div key={i} style={{
                    display: "flex", gap: "16px", alignItems: "flex-start",
                    padding: "14px 16px", background: colors.deep, borderRadius: "10px",
                  }}>
                    <span style={{
                      fontSize: "10px", textTransform: "uppercase", letterSpacing: "1px",
                      color: colors.accent, fontWeight: 700, minWidth: "100px", paddingTop: "3px",
                    }}>{ex.context}</span>
                    <span style={{ color: colors.text, fontSize: "14px", lineHeight: 1.6 }}>{ex.copy}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Product Naming Tab */}
        {activeTab === "naming" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div style={{
              background: colors.surface, borderRadius: "16px", padding: "28px",
              border: `1px solid rgba(123, 111, 240, 0.1)`,
            }}>
              <h3 style={{ fontSize: "13px", textTransform: "uppercase", letterSpacing: "2px", color: colors.textDim, marginBottom: "8px", fontWeight: 600 }}>Naming Philosophy</h3>
              <p style={{ color: colors.textMuted, fontSize: "14px", lineHeight: 1.7, marginBottom: "24px" }}>
                Brand the platform. Don't over-brand the features. Developers trust tools that use familiar terminology. Reserve branded language for your one core concept: a group of coordinated agents is a <strong style={{ color: colors.accent }}>Swirl</strong>.
              </p>
              <div style={{
                display: "grid", gridTemplateColumns: "1fr 1fr 2fr",
                gap: "0", borderRadius: "10px", overflow: "hidden",
                border: `1px solid rgba(123, 111, 240, 0.15)`,
              }}>
                {/* Header */}
                {["Element", "Term", "Notes"].map(h => (
                  <div key={h} style={{
                    padding: "12px 16px", background: "rgba(123, 111, 240, 0.12)",
                    fontSize: "11px", textTransform: "uppercase", letterSpacing: "1.5px",
                    fontWeight: 700, color: colors.accent,
                  }}>{h}</div>
                ))}
                {/* Rows */}
                {namingSystem.map((row, i) => (
                  [row.element, row.term, row.note].map((cell, j) => (
                    <div key={`${i}-${j}`} style={{
                      padding: "12px 16px", fontSize: "13px", lineHeight: 1.5,
                      color: j === 1 ? colors.teal : colors.textMuted,
                      fontWeight: j === 1 ? 700 : 400,
                      fontFamily: j === 1 ? "monospace" : "inherit",
                      background: i % 2 === 0 ? "rgba(255,255,255,0.02)" : "transparent",
                      borderTop: `1px solid rgba(123, 111, 240, 0.06)`,
                    }}>{cell}</div>
                  ))
                ))}
              </div>
            </div>

            <div style={{
              background: colors.surface, borderRadius: "16px", padding: "28px",
              border: `1px solid rgba(123, 111, 240, 0.1)`,
            }}>
              <h3 style={{ fontSize: "13px", textTransform: "uppercase", letterSpacing: "2px", color: colors.textDim, marginBottom: "16px", fontWeight: 600 }}>Usage Examples</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {[
                  '"Create a new swirl with 3 agents for sprint planning"',
                  '"Add the Linear connector to your space"',
                  '"This template includes a code review swirl with 4 agents"',
                  '"Your Pro plan includes 2,000 runs per month"',
                  '"Deploy your swirl to production with one click"',
                ].map((ex, i) => (
                  <div key={i} style={{
                    padding: "12px 16px", background: colors.deep, borderRadius: "8px",
                    fontFamily: "monospace", fontSize: "13px", color: colors.teal,
                    border: `1px solid rgba(62, 207, 180, 0.08)`,
                  }}>{ex}</div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Launch Copy Tab */}
        {activeTab === "launch" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* Landing Page Hero */}
            <div style={{
              background: `linear-gradient(135deg, ${colors.surface} 0%, rgba(123,111,240,0.08) 100%)`,
              borderRadius: "16px", padding: "48px 36px", textAlign: "center",
              border: `1px solid rgba(123, 111, 240, 0.15)`,
            }}>
              <div style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "2px", color: colors.accent, fontWeight: 700, marginBottom: "16px" }}>Landing Page Hero</div>
              <h1 style={{
                fontSize: "36px", fontWeight: 800, lineHeight: 1.15, marginBottom: "16px",
                background: `linear-gradient(135deg, ${colors.text} 0%, ${colors.accentLight} 100%)`,
                WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
              }}>
                Stop babysitting AI agents.<br />Start orchestrating them.
              </h1>
              <p style={{ color: colors.textMuted, fontSize: "17px", lineHeight: 1.6, maxWidth: "500px", margin: "0 auto 28px" }}>
                Swrly lets you build teams of Claude Code agents, connect them to your tools, and ship workflows that actually run your business.
              </p>
              <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
                <div style={{
                  padding: "12px 28px", borderRadius: "8px", fontWeight: 700, fontSize: "15px",
                  background: `linear-gradient(135deg, ${colors.accent}, #6055D0)`,
                  color: "#fff", boxShadow: `0 4px 24px ${colors.accentGlow}`,
                }}>Start building free</div>
                <div style={{
                  padding: "12px 28px", borderRadius: "8px", fontWeight: 600, fontSize: "15px",
                  background: "rgba(255,255,255,0.05)", color: colors.text,
                  border: `1px solid rgba(255,255,255,0.1)`,
                }}>Watch demo</div>
              </div>
            </div>

            {/* Product Hunt */}
            <div style={{
              background: colors.surface, borderRadius: "16px", padding: "28px",
              border: `1px solid rgba(123, 111, 240, 0.1)`,
            }}>
              <div style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "2px", color: colors.coral, fontWeight: 700, marginBottom: "12px" }}>Product Hunt Tagline</div>
              <div style={{ fontSize: "20px", fontWeight: 700, color: colors.text, marginBottom: "12px" }}>
                Swrly — Build AI agent teams that run your dev workflow
              </div>
              <p style={{ color: colors.textMuted, fontSize: "14px", lineHeight: 1.7 }}>
                Create Claude Code agents, wire them to Linear, Slack, and any API, and orchestrate them into teams that handle sprint planning, code review, bug triage, and more. Start with templates or build your own from scratch.
              </p>
            </div>

            {/* Hacker News */}
            <div style={{
              background: colors.surface, borderRadius: "16px", padding: "28px",
              border: `1px solid rgba(123, 111, 240, 0.1)`,
            }}>
              <div style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "2px", color: colors.teal, fontWeight: 700, marginBottom: "12px" }}>Show HN Post</div>
              <div style={{ fontSize: "18px", fontWeight: 700, color: colors.text, marginBottom: "12px" }}>
                Show HN: Swrly — I built an agent orchestration platform for my business, now it's a SaaS
              </div>
              <div style={{
                padding: "16px", background: colors.deep, borderRadius: "10px",
                fontFamily: "monospace", fontSize: "13px", color: colors.textMuted, lineHeight: 1.8,
              }}>
                Hey HN, I'm [name] and I built Swrly because I was tired of manually stitching together Claude agents for my own dev workflows.<br /><br />
                The core idea: create agents, define how they coordinate as a team ("swirl"), connect to tools like Linear and Slack via API, and let them handle repetitive work. I've been using it internally for 6 months and now it's open for beta.<br /><br />
                Stack: [your stack]. Built on Claude Code agents.<br />
                Free tier: 3 agents, 100 runs/month.<br /><br />
                Would love feedback from anyone orchestrating AI agents today. What's broken about your current setup?
              </div>
            </div>

            {/* First tweet */}
            <div style={{
              background: colors.surface, borderRadius: "16px", padding: "28px",
              border: `1px solid rgba(123, 111, 240, 0.1)`,
            }}>
              <div style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "2px", color: colors.accent, fontWeight: 700, marginBottom: "12px" }}>Launch Tweet Thread (First Tweet)</div>
              <div style={{
                padding: "16px", background: colors.deep, borderRadius: "10px",
                fontSize: "15px", color: colors.text, lineHeight: 1.7,
              }}>
                I spent 6 months building an AI agent orchestration system for my own business.<br /><br />
                Today I'm launching it as a product.<br /><br />
                Meet Swrly — build teams of Claude Code agents, connect them to your tools, and let them handle the work you keep putting off.<br /><br />
                Here's how it works (thread) 🧵
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div style={{
          marginTop: "60px", paddingTop: "24px",
          borderTop: `1px solid rgba(123, 111, 240, 0.08)`,
          textAlign: "center",
        }}>
          <span style={{ fontSize: "12px", color: colors.textDim }}>
            Swrly Brand Kit — Register swrly.com and swrly.ai today
          </span>
        </div>
      </div>
    </div>
  );
};

export default SwrlyBrandPage;