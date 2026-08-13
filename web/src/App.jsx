const modules = [
  { name: "Dashboard", detail: "Streamlit Haupt-GUI auf Port 8501" },
  { name: "Admin", detail: "Flask Setup + Service-Status auf Port 5000" },
  { name: "Archiv", detail: "Ein Archiver: DestinyChatSorterPro" },
  { name: "Live-Check", detail: "tools/live_check.py" },
];

export default function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        margin: 0,
        background: "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)",
        color: "#e5e7eb",
        fontFamily: "Segoe UI, system-ui, sans-serif",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <main style={{ textAlign: "center", padding: 32, maxWidth: 720 }}>
        <h1 style={{ fontSize: 48, marginBottom: 12 }}>Destiny OS</h1>
        <p style={{ fontSize: 20, color: "#7dd3fc" }}>
          KI-betriebenes Wissensmanagement — Praesentationsseite, kein zweites Backend
        </p>
        <div style={{ marginTop: 32 }}>
          <a href="http://localhost:8501" style={{ color: "#86efac", margin: "0 16px" }}>
            Dashboard :8501
          </a>
          <a href="http://localhost:5000" style={{ color: "#86efac", margin: "0 16px" }}>
            Admin :5000
          </a>
          <a href="http://localhost:5000/admin" style={{ color: "#86efac", margin: "0 16px" }}>
            Service-Status
          </a>
        </div>
        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: 12,
            marginTop: 36,
            textAlign: "left",
          }}
        >
          {modules.map((item) => (
            <article
              key={item.name}
              style={{ background: "#111827", borderRadius: 12, padding: 14 }}
            >
              <h2 style={{ margin: "0 0 6px", fontSize: 16 }}>{item.name}</h2>
              <p style={{ margin: 0, color: "#9ca3af", fontSize: 14 }}>{item.detail}</p>
            </article>
          ))}
        </section>
        <p style={{ fontSize: 14, color: "#6b7280", marginTop: 28 }}>
          v1.3.0 · Christian Schmitt · Landingpage ohne eigenes API
        </p>
      </main>
    </div>
  );
}
