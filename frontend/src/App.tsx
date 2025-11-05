import { Toaster } from 'react-hot-toast'
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Scraper from './pages/Scraper'
import Search from './pages/Search'
import Timeline from './pages/Timeline'
import TopicDetail from './pages/TopicDetail'
import Topics from './pages/Topics'

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Toaster position="top-right" />
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/topics" element={<Topics />} />
          <Route path="/topics/:topicId" element={<TopicDetail />} />
          <Route path="/search" element={<Search />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/scraper" element={<Scraper />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
