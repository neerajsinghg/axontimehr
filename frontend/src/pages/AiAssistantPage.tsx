import React, { useState } from 'react';
import { aiApi, AIQueryResponse } from '../services/api/ai';

export const AiAssistantPage: React.FC = () => {
  const [queryText, setQueryText] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<Array<{ role: 'user' | 'assistant'; text: string; trace?: AIQueryResponse }>>([
    {
      role: 'assistant',
      text: "Hello! I am your AxonTimeHR Intelligence Assistant. Ask me natural language questions about headcount, attrition rates, payroll spend, recruitment pipelines, or skill gaps.",
    },
  ]);

  const handleSendQuery = async (customText?: string) => {
    const textToSubmit = customText || queryText;
    if (!textToSubmit.trim() || loading) return;

    setChatHistory((prev) => [...prev, { role: 'user', text: textToSubmit }]);
    if (!customText) setQueryText('');
    setLoading(true);

    try {
      const response = await aiApi.queryAssistant(textToSubmit);
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: response.answer_text,
          trace: response,
        },
      ]);
    } catch (err: any) {
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: "I encountered an error retrieving authorized context parameters. Please verify server connectivity.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif', maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ margin: 0 }}>🤖 AxonTimeHR Controlled AI HR Intelligence Assistant</h2>
        <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
          Natural Language HR Intelligence query engine. Interacts through strict RBAC-enforced tool execution with ZERO direct database access.
        </p>
      </div>

      {/* Suggested Queries */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
        {[
          "What is our organizational attrition rate?",
          "Show current active headcount vs planned targets",
          "What is our monthly gross payroll spend?",
          "How many open job listings and pipeline candidates exist?",
        ].map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSendQuery(q)}
            style={{
              padding: '6px 14px',
              borderRadius: '16px',
              border: '1px solid #BFDBFE',
              background: '#EFF6FF',
              color: '#1E40AF',
              fontSize: '12px',
              fontWeight: 'bold',
              cursor: 'pointer',
            }}
          >
            💡 "{q}"
          </button>
        ))}
      </div>

      {/* Chat History Box */}
      <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', minHeight: '400px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxHeight: '500px', overflowY: 'auto', paddingRight: '8px' }}>
          {chatHistory.map((msg, idx) => (
            <div
              key={idx}
              style={{
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%',
                background: msg.role === 'user' ? '#2563EB' : '#F3F4F6',
                color: msg.role === 'user' ? '#fff' : '#111827',
                padding: '14px',
                borderRadius: '12px',
                lineHeight: '1.5',
                fontSize: '14px',
              }}
            >
              <div style={{ fontWeight: 'bold', fontSize: '11px', marginBottom: '4px', opacity: 0.8 }}>
                {msg.role === 'user' ? 'You' : 'AxonTimeHR AI Engine'}
              </div>
              <div>{msg.text}</div>

              {msg.trace && (
                <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid #E5E7EB', fontSize: '11px', color: '#4B5563' }}>
                  <div style={{ fontWeight: 'bold', color: '#059669', marginBottom: '2px' }}>
                    🛡️ {msg.trace.confidence_level}
                  </div>
                  <div>
                    Authorized Tools Executed:{' '}
                    <b>{msg.trace.tools_invoked.map((t) => t.tool_name).join(', ') || 'get_executive_summary'}</b> ({msg.trace.latency_ms}ms)
                  </div>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ alignSelf: 'flex-start', background: '#F3F4F6', color: '#6B7280', padding: '12px 18px', borderRadius: '12px', fontSize: '13px', fontStyle: 'italic' }}>
              🧠 Executing authorized backend analytics tools...
            </div>
          )}
        </div>

        {/* Input Form */}
        <form
          onSubmit={(e) => { e.preventDefault(); handleSendQuery(); }}
          style={{ display: 'flex', gap: '8px', marginTop: '20px' }}
        >
          <input
            type="text"
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            placeholder="Ask a question (e.g. What is the current attrition rate in Sales?)"
            style={{ flex: 1, padding: '10px 14px', borderRadius: '6px', border: '1px solid #D1D5DB', fontSize: '14px' }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{ padding: '10px 20px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            Send Question
          </button>
        </form>
      </div>
    </div>
  );
};
