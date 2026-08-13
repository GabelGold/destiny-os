const modules = [
  { name: "Chat-Archiv", detail: "Chats + Code-Blöcke unter destiny_archive" },
  { name: "Streamlit GUI", detail: "Dashboard auf Port 8501" },
  { name: "Flask Setup", detail: "Profil, Tools, Archiv auf Port 5000" },
  { name: "Live-Check", detail: "tools/live_check.py – Struktur, Syntax, Hashes" },
  { name: "8 Services", detail: "systemd unter Linux, auf Windows nicht aktiv" },
  { name: "Memory Layer", detail: "SQLite-Notizspeicher destiny_memory.sqlite" },
];

const commands = [
  "python tools\\live_check.py",
  "python -m streamlit run src\\destiny_gui.py",
  "python src\\destiny_setup.py",
  "cd web && npm install && npm run dev",
];

export default function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        margin: 0,
        background: "#070b12",
        color: "#f5f5f5",
        fontFamily: "Segoe UI, system-ui, sans-serif",
      }}
    >
      <header
        style={{
          padding: "28px 32px",
          background: "#111827",
          borderBottom: "1px solid #1f2937",
        }}
      >
        <div style={{ fontSize: 28, fontWeight: 700 }}>Destiny OS</div>
        <div style={{ color: "#9ca3af", marginTop: 6 }}>
          Offline Survival System · v1.0.0 · Christian Schmitt · 13. August 2026
        </div>
      </header>

      <main style={{ maxWidth: 1100, margin: "0 auto", padding: 32 }}>
        <p style={{ fontSize: 18, lineHeight: 1.5, maxWidth: 720 }}>
          Python-Schicht für Archiv, Setup und lokale Orchestrierung. Der
          produktive Kern liegt unter{" "}
          <code>I:\\Offline Survival System Emulator\\DESTINY-OS_PROD\\</code>
        </p>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: 16,
            marginTop: 28,
          }}
        >
          {modules.map((item) => (
            <article
              key={item.name}
              style={{
                background: "#1f2937",
                borderRadius: 12,
                padding: "16px 18px",
              }}
            >
              <h2 style={{ margin: "0 0 8px", fontSize: 18 }}>{item.name}</h2>
              <p style={{ margin: 0, color: "#d1d5db" }}>{item.detail}</p>
            </article>
          ))}
        </section>

        <section style={{ marginTop: 36 }}>
          <h2>Startbefehle</h2>
          <pre
            style={{
              background: "#020617",
              border: "1px solid #1f2937",
              borderRadius: 12,
              padding: 16,
              overflowX: "auto",
            }}
          >
            {commands.join("\n")}
          </pre>
        </section>
      </main>
    </div>
  );
}
