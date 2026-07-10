import { NavLink, Outlet } from 'react-router-dom'

const links = [['/', '首页'], ['/new', '新建检查'], ['/history', '历史记录'], ['/rules', '规则管理']]
export default function Layout() {
  return <div className="app-shell">
    <a className="skip-link" href="#main">跳到主要内容</a>
    <header className="topbar"><NavLink className="brand" to="/" aria-label="SubmitReady 首页"><span className="brand-mark">SR</span><span><b>SubmitReady</b><small>提交前检查台</small></span></NavLink><nav aria-label="主导航">{links.map(([to, label]) => <NavLink key={to} to={to} end={to === '/'}>{label}</NavLink>)}</nav></header>
    <main id="main"><Outlet /></main>
    <footer><span>SubmitReady · 确定性检查，不依赖 AI</span><a href="/docs" target="_blank" rel="noreferrer">API 文档</a></footer>
  </div>
}
