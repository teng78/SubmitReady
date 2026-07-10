import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import NewRunPage from './pages/NewRunPage'
import ProgressPage from './pages/ProgressPage'
import ReportPage from './pages/ReportPage'
import HistoryPage from './pages/HistoryPage'
import RulesPage from './pages/RulesPage'

export default function App() { return <Routes><Route element={<Layout />}><Route index element={<HomePage />} /><Route path="new" element={<NewRunPage />} /><Route path="runs/:id" element={<ProgressPage />} /><Route path="runs/:id/report" element={<ReportPage />} /><Route path="history" element={<HistoryPage />} /><Route path="rules" element={<RulesPage />} /><Route path="*" element={<section className="page narrow"><p className="eyebrow">404</p><h1>页面不存在</h1><a className="button" href="/">返回首页</a></section>} /></Route></Routes> }
