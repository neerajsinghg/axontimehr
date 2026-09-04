import React, { useState, useEffect } from 'react';
import { financialApi, ExpenseCategory, ExpenseClaim } from '../services/api/financial';

export const ExpensesPage: React.FC = () => {
  const [claims, setClaims] = useState<ExpenseClaim[]>([]);
  const [categories, setCategories] = useState<ExpenseCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Form State
  const [claimDate, setClaimDate] = useState(new Date().toISOString().split('T')[0]);
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [amount, setAmount] = useState('');
  const [merchant, setMerchant] = useState('');
  const [receiptId, setReceiptId] = useState<string | undefined>();
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [cRes, catRes] = await Promise.all([
        financialApi.getClaims(),
        financialApi.getCategories(),
      ]);
      setClaims(cRes.data);
      setCategories(catRes.data);
      if (catRes.data.length > 0) setCategoryId(catRes.data[0].id);
    } catch (err) {
      console.error('Failed to load expense data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    try {
      setUploading(true);
      const res = await financialApi.uploadReceipt(e.target.files[0]);
      setReceiptId(res.data.id);
      alert('Receipt uploaded securely!');
    } catch (err) {
      alert('Receipt upload failed. Ensure valid file type (PDF/JPG/PNG) under 10MB.');
    } finally {
      setUploading(false);
    }
  };

  const handleCreateClaim = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        claim_date: claimDate,
        description,
        currency: 'INR',
        items: [
          {
            category_id: categoryId,
            expense_date: claimDate,
            amount: parseFloat(amount),
            merchant,
            receipt_file_id: receiptId,
          },
        ],
      };
      await financialApi.createClaim(payload);
      setShowModal(false);
      setDescription('');
      setAmount('');
      setMerchant('');
      setReceiptId(undefined);
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Error submitting claim');
    }
  };

  const handleSubmitClaim = async (claimId: string) => {
    try {
      await financialApi.submitClaim(claimId);
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to submit claim for approval');
    }
  };

  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [catName, setCatName] = useState('');
  const [catCode, setCatCode] = useState('');
  const [catMax, setCatMax] = useState('');

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financialApi.createCategory({
        name: catName,
        code: catCode.toUpperCase().replace(/\s+/g, '_'),
        max_amount: catMax ? parseFloat(catMax) : undefined,
        requires_receipt: true,
        requires_approval: true,
      });
      setShowCategoryModal(false);
      setCatName('');
      setCatCode('');
      setCatMax('');
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to create category');
    }
  };

  // Filtered Claims
  const filteredClaims = statusFilter === 'ALL'
    ? claims
    : claims.filter(c => c.status === statusFilter);

  // Policy Limit Check Helper
  const selectedCat = categories.find(c => c.id === categoryId);
  const enteredAmt = parseFloat(amount) || 0;
  const isOverPolicyLimit = selectedCat?.max_amount ? enteredAmt > selectedCat.max_amount : false;

  // KPI Calculations
  const pendingAmt = claims.filter(c => c.status === 'SUBMITTED').reduce((acc, c) => acc + (c.total_amount || 0), 0);
  const approvedAmt = claims.filter(c => c.status === 'APPROVED' || c.status === 'DISBURSED').reduce((acc, c) => acc + (c.total_amount || 0), 0);

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>💳 Expense Claims & Reimbursements</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
            Submit, approve, and track employee expense reimbursements with receipt verification.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setShowCategoryModal(true)}
            style={{ padding: '10px 18px', background: '#4B5563', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            + Add Expense Category
          </button>
          <button
            onClick={() => setShowModal(true)}
            style={{ padding: '10px 18px', background: '#3B82F6', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            + New Expense Claim
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #3B82F6' }}>
          <p style={{ margin: 0, fontSize: '13px', color: '#6B7280' }}>Total Claims Filed</p>
          <h2 style={{ margin: '6px 0 0 0', color: '#1E40AF' }}>{claims.length} Claims</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #F59E0B' }}>
          <p style={{ margin: 0, fontSize: '13px', color: '#6B7280' }}>Pending Approval Value</p>
          <h2 style={{ margin: '6px 0 0 0', color: '#B45309' }}>₹ {pendingAmt.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #10B981' }}>
          <p style={{ margin: 0, fontSize: '13px', color: '#6B7280' }}>Approved / Reimbursed Total</p>
          <h2 style={{ margin: '6px 0 0 0', color: '#065F46' }}>₹ {approvedAmt.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</h2>
        </div>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        {['ALL', 'DRAFT', 'SUBMITTED', 'APPROVED', 'DISBURSED', 'REJECTED'].map((st) => (
          <button
            key={st}
            onClick={() => setStatusFilter(st)}
            style={{
              padding: '6px 14px',
              borderRadius: '20px',
              border: 'none',
              fontSize: '12px',
              fontWeight: 'bold',
              cursor: 'pointer',
              background: statusFilter === st ? '#3B82F6' : '#E5E7EB',
              color: statusFilter === st ? '#fff' : '#374151',
            }}
          >
            {st}
          </button>
        ))}
      </div>

      {loading ? (
        <p>Loading expenses...</p>
      ) : filteredClaims.length === 0 ? (
        <div style={{ background: '#fff', padding: '40px', borderRadius: '8px', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <p style={{ color: '#6B7280', margin: 0 }}>No expense claims found for this status filter.</p>
        </div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <thead>
            <tr style={{ background: '#F3F4F6', textAlign: 'left', borderBottom: '1px solid #E5E7EB' }}>
              <th style={{ padding: '12px 16px' }}>Claim #</th>
              <th style={{ padding: '12px 16px' }}>Date</th>
              <th style={{ padding: '12px 16px' }}>Description</th>
              <th style={{ padding: '12px 16px' }}>Total Amount</th>
              <th style={{ padding: '12px 16px' }}>Status</th>
              <th style={{ padding: '12px 16px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredClaims.map((claim) => (
              <tr key={claim.id} style={{ borderBottom: '1px solid #F3F4F6' }}>
                <td style={{ padding: '12px 16px', fontWeight: 'bold' }}>{claim.claim_number}</td>
                <td style={{ padding: '12px 16px' }}>{claim.claim_date}</td>
                <td style={{ padding: '12px 16px' }}>{claim.description}</td>
                <td style={{ padding: '12px 16px', fontWeight: '600' }}>₹ {claim.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '600',
                    background: claim.status === 'APPROVED' ? '#D1FAE5' : claim.status === 'DRAFT' ? '#FEF3C7' : '#E0E7FF',
                    color: claim.status === 'APPROVED' ? '#065F46' : claim.status === 'DRAFT' ? '#92400E' : '#3730A3',
                  }}>
                    {claim.status}
                  </span>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  {claim.status === 'DRAFT' && (
                    <button
                      onClick={() => handleSubmitClaim(claim.id)}
                      style={{ padding: '6px 12px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                    >
                      Submit
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '450px' }}>
            <h3>Create New Expense Claim</h3>
            <form onSubmit={handleCreateClaim}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Expense Category</label>
                <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name} (Max ₹ {c.max_amount ? c.max_amount.toLocaleString('en-IN') : 'No Limit'})</option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Claim Date</label>
                <input type="date" value={claimDate} onChange={(e) => setClaimDate(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Merchant / Vendor Name</label>
                <input type="text" value={merchant} onChange={(e) => setMerchant(e.target.value)} placeholder="e.g. Uber / Indigo Airlines" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Amount (₹)</label>
                <input type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="1500.00" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
                {isOverPolicyLimit && (
                  <p style={{ color: '#EF4444', fontSize: '12px', margin: '4px 0 0 0', fontWeight: 'bold' }}>
                    ⚠️ Warning: Amount exceeds Category Policy Limit (Max ₹ {selectedCat?.max_amount?.toLocaleString('en-IN')}). Claim requires special manager approval.
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Claim Purpose / Description</label>
                <textarea rows={2} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Client meeting travel expenses..." style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Upload Bill / Receipt File</label>
                <input type="file" onChange={handleFileUpload} accept="image/*,application/pdf" style={{ fontSize: '13px' }} />
                {uploading && <span style={{ fontSize: '12px', color: '#3B82F6', marginLeft: '8px' }}>Uploading...</span>}
                {receiptId && <span style={{ fontSize: '12px', color: '#10B981', fontWeight: 'bold', marginLeft: '8px' }}>✓ Receipt Attached</span>}
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#3B82F6', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Save Draft Claim</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showCategoryModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '400px' }}>
            <h3>Create Expense Category</h3>
            <form onSubmit={handleCreateCategory}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Category Name</label>
                <input type="text" value={catName} onChange={(e) => setCatName(e.target.value)} placeholder="e.g. Flight Tickets" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Category Code</label>
                <input type="text" value={catCode} onChange={(e) => setCatCode(e.target.value)} placeholder="e.g. FLIGHTS" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Max Daily Limit (₹)</label>
                <input type="number" value={catMax} onChange={(e) => setCatMax(e.target.value)} placeholder="10000" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowCategoryModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#4B5563', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Create Category</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
