import { PropsWithChildren } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

export const DashboardLayout: React.FC<PropsWithChildren> = ({ children }) => {
  const { user, logout } = useAuth();

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar__brand">
          <span className="sidebar__logo">GeM</span>
          <span className="sidebar__title">Bid Analyzer</span>
        </div>
        <nav className="sidebar__nav">
          <Link to="/" className="sidebar__link">
            Dashboard
          </Link>
          <a
            href="https://gem.gov.in/"
            target="_blank"
            rel="noreferrer"
            className="sidebar__link sidebar__link--secondary"
          >
            GeM Portal
          </a>
        </nav>
      </aside>
      <div className="main">
        <header className="topbar">
          <div>
            <h1 className="topbar__title">Tender Intelligence</h1>
            <p className="topbar__subtitle">Smart summaries, compliance insights, and collaboration tools</p>
          </div>
          <div className="topbar__account">
            <div className="topbar__avatar">{user?.email[0]?.toUpperCase()}</div>
            <div className="topbar__meta">
              <span className="topbar__name">{user?.fullName ?? user?.email}</span>
              <span className="topbar__org">{user?.organization ?? "Administrator"}</span>
            </div>
            <button className="btn btn--ghost" onClick={logout}>
              Logout
            </button>
          </div>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
};
