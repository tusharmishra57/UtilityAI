import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { LogOut, Zap, CreditCard, MessageSquare, Send } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);
  const [consumption, setConsumption] = useState([]);
  const [bills, setBills] = useState([]);
  const [aiQuestion, setAiQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<{q: string, a: string}[]>([]);
  const [loadingAi, setLoadingAi] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const userRes = await api.get('/auth/me');
      setUser(userRes.data);
      
      const consRes = await api.get('/consumption');
      setConsumption(consRes.data);
      
      const billsRes = await api.get('/bills');
      setBills(billsRes.data);
    } catch (err) {
      navigate('/');
    }
  };

  const handlePay = async (billId: number) => {
    try {
      await api.post('/payments', { bill_id: billId });
      alert('Payment Successful!');
      fetchData();
    } catch (err) {
      alert('Payment Failed');
    }
  };

  const askAi = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiQuestion.trim()) return;
    
    setLoadingAi(true);
    const q = aiQuestion;
    setAiQuestion('');
    
    try {
      const res = await api.post('/ai/ask', { question: q });
      setChatHistory(prev => [...prev, { q, a: res.data.answer }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { q, a: 'Sorry, AI service is currently unavailable.' }]);
    } finally {
      setLoadingAi(false);
    }
  };

  if (!user) return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row font-sans">
      
      {/* Sidebar */}
      <aside className="w-full md:w-64 bg-slate-900 text-white flex flex-col shadow-xl z-10">
        <div className="p-6">
          <h1 className="text-2xl font-bold tracking-wider flex items-center gap-2">
            <Zap className="text-yellow-400" /> UtilityAI
          </h1>
          <p className="text-slate-400 text-sm mt-2">Welcome, {user.name}</p>
        </div>
        <nav className="flex-1 px-4 space-y-2 mt-4">
          <a href="#" className="flex items-center gap-3 bg-white/10 px-4 py-3 rounded-lg text-sm font-medium transition-colors">
            Dashboard
          </a>
        </nav>
        <div className="p-4">
          <button 
            onClick={() => { localStorage.removeItem('token'); navigate('/'); }}
            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm font-medium"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-6 md:p-10 overflow-y-auto bg-slate-50">
        
        {/* Consumption Chart */}
        <section className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 mb-8 transform transition hover:shadow-md">
          <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
            Consumption History
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={consumption}>
                <XAxis dataKey="month" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Line type="monotone" dataKey="consumption_kwh" stroke="#3b82f6" strokeWidth={3} dot={{r: 4}} activeDot={{r: 6}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Bills Grid */}
        <section className="mb-8">
          <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
            Recent Bills
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {bills.map((bill: any) => (
              <div key={bill.id} className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 flex flex-col transition hover:shadow-md hover:-translate-y-1">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <p className="text-sm font-medium text-slate-500">{bill.billing_month}</p>
                    <h3 className="text-2xl font-bold text-slate-800">Rs {bill.amount}</h3>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${bill.status === 'PAID' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {bill.status}
                  </span>
                </div>
                <div className="text-sm text-slate-600 space-y-1 flex-1">
                  <p>Usage: <span className="font-semibold">{bill.consumption_kwh} kWh</span></p>
                  <p>Due: <span className="font-semibold">{bill.due_date}</span></p>
                </div>
                {bill.status === 'UNPAID' && (
                  <button 
                    onClick={() => handlePay(bill.id)}
                    className="mt-6 w-full flex items-center justify-center gap-2 bg-slate-900 text-white py-2 rounded-xl font-medium hover:bg-slate-800 transition-colors"
                  >
                    <CreditCard size={18} /> Pay Now
                  </button>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* AI Assistant */}
        <section className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col h-[500px]">
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <MessageSquare size={20} /> Energy Assist AI
            </h2>
          </div>
          
          <div className="flex-1 p-6 overflow-y-auto bg-slate-50/50 space-y-6">
            {chatHistory.length === 0 && (
              <div className="text-center text-slate-400 mt-10">
                <p>Ask me anything about your utility bills, consumption trends, or energy saving tips!</p>
              </div>
            )}
            
            {chatHistory.map((chat, idx) => (
              <div key={idx} className="space-y-4">
                <div className="flex justify-end">
                  <div className="bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-5 py-3 max-w-[80%] shadow-sm">
                    {chat.q}
                  </div>
                </div>
                <div className="flex justify-start">
                  <div className="bg-white border border-slate-200 text-slate-800 rounded-2xl rounded-tl-sm px-5 py-3 max-w-[80%] shadow-sm">
                    {chat.a}
                  </div>
                </div>
              </div>
            ))}
            {loadingAi && (
              <div className="flex justify-start animate-pulse">
                 <div className="bg-white border border-slate-200 text-slate-500 rounded-2xl rounded-tl-sm px-5 py-3 shadow-sm">
                   Thinking...
                 </div>
              </div>
            )}
          </div>
          
          <form onSubmit={askAi} className="p-4 bg-white border-t border-slate-100 flex gap-3">
            <input 
              type="text" 
              className="flex-1 bg-slate-100 border-none rounded-xl px-5 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              placeholder="Why is my bill higher this month?"
              value={aiQuestion}
              onChange={(e) => setAiQuestion(e.target.value)}
            />
            <button 
              type="submit"
              disabled={loadingAi || !aiQuestion.trim()}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white p-3 rounded-xl transition-colors shadow-sm flex items-center justify-center"
            >
              <Send size={20} />
            </button>
          </form>
        </section>
        
      </main>
    </div>
  );
}
