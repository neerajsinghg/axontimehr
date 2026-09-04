import React, { useState } from 'react';
import { Bot, Send, Sparkles, User } from 'lucide-react';
import { intelligenceBiApi, AICopilotChatResponse } from '../services/api/intelligenceBi';

export const AiCopilotPage: React.FC = () => {
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'assistant'; text: string; kpis?: any[] }>>([
    {
      sender: 'assistant',
      text: 'Hello! I am AxonTime AI Copilot. Ask me anything about headcount, attendance adherence, payroll costs, overtime, compliance deadlines, or attrition forecasting.',
      kpis: [
        { label: 'Active Headcount', value: '142', change: '+3 this month' },
        { label: 'Monthly Payroll', value: '₹18,450,000', change: '+2.4%' },
        { label: 'Attendance Rate', value: '94.2%', change: '+1.1%' }
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [convId, setConvId] = useState<string | undefined>(undefined);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userText = input;
    setInput('');
    setMessages((prev) => [...prev, { sender: 'user', text: userText }]);
    setLoading(true);

    try {
      const res: AICopilotChatResponse = await intelligenceBiApi.sendCopilotMessage({
        message_text: userText,
        conversation_id: convId
      });
      setConvId(res.conversation_id);
      setMessages((prev) => [
        ...prev,
        { sender: 'assistant', text: res.reply_text, kpis: res.kpi_cards }
      ]);
    } catch (err) {
      console.error('Failed to send copilot message', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <Bot className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          AxonTime AI Copilot & Decision Support Assistant
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Conversational workforce intelligence with RBAC multi-tenant data access control.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden flex flex-col h-[600px]">
        {/* Chat Feed */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {messages.map((m, idx) => (
            <div key={idx} className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              {m.sender === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center shrink-0">
                  <Sparkles className="w-4 h-4" />
                </div>
              )}
              <div className={`max-w-2xl p-4 rounded-xl text-sm ${m.sender === 'user' ? 'bg-indigo-600 text-white' : 'bg-slate-50 dark:bg-slate-700/50 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-600'}`}>
                <p className="whitespace-pre-line">{m.text}</p>
                {m.kpis && m.kpis.length > 0 && (
                  <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-200 dark:border-slate-600">
                    {m.kpis.map((k: any, i: number) => (
                      <div key={i} className="bg-white dark:bg-slate-800 p-2.5 rounded border border-slate-200 dark:border-slate-700 text-center">
                        <div className="text-[10px] text-slate-400 uppercase font-semibold">{k.label}</div>
                        <div className="text-base font-bold text-slate-900 dark:text-white">{k.value}</div>
                        <div className="text-[10px] text-emerald-600">{k.change}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {m.sender === 'user' && (
                <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-2 items-center text-xs text-slate-400 font-semibold italic">
              <Sparkles className="w-4 h-4 animate-spin text-indigo-500" />
              AxonTime AI Copilot processing intent...
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="p-4 bg-slate-50 dark:bg-slate-700/30 border-t border-slate-200 dark:border-slate-700 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask AI Copilot (e.g. 'Show monthly payroll breakdown' or 'Check overtime anomalies')..."
            className="flex-1 p-3 border border-slate-300 rounded-lg dark:bg-slate-800 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </form>
      </div>
    </div>
  );
};
