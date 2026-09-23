"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Shield,
  CreditCard,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  Lock,
  Globe,
  Mail,
  User,
  Building,
  Sparkles,
  Receipt,
} from "lucide-react";
import { api, AuditRequest } from "@/lib/api";

export default function AuditRequestPage() {
  const [step, setStep] = useState<"form" | "payment" | "success">("form");

  // Form Fields
  const [targetUrl, setTargetUrl] = useState("");
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [organization, setOrganization] = useState("");
  const [scopeNotes, setScopeNotes] = useState("");
  const [authorized, setAuthorized] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Payment states
  const [createdAudit, setCreatedAudit] = useState<AuditRequest | null>(null);
  const [paymentMethod, setPaymentMethod] = useState("upi");
  const [paying, setPaying] = useState(false);
  const [paymentReceipt, setPaymentReceipt] = useState<any>(null);

  // Step 1: Submit Details
  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUrl.trim() || !contactName.trim() || !contactEmail.trim()) {
      setError("Please fill in all required fields (Website URL, Name, and Email).");
      return;
    }
    if (!authorized) {
      setError("You must confirm you are legally authorized to request a security assessment of this target.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await api.createAuditRequest({
        target_url: targetUrl.trim(),
        contact_name: contactName.trim(),
        contact_email: contactEmail.trim(),
        organization: organization.trim() || undefined,
        scope_notes: scopeNotes.trim() || undefined,
        authorized: true,
      });
      setCreatedAudit(res);
      setStep("payment");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to submit audit request. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Process Payment
  const handlePayment = async () => {
    if (!createdAudit) return;
    setPaying(true);
    setError("");

    try {
      const receipt = await api.payAuditRequest(createdAudit.id, paymentMethod);
      setPaymentReceipt(receipt);
      setStep("success");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Payment processing failed. Please try again.");
    } finally {
      setPaying(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-4">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Professional Security Assessment</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          Book Advanced Website Security Audit
        </h1>
        <p className="text-slate-400 text-sm sm:text-base mt-2 max-w-xl mx-auto">
          Comprehensive manual and automated audit conducted by experienced security engineers. Fixed price of ₹1,999 per domain.
        </p>
      </div>

      {/* Progress Indicators */}
      <div className="flex items-center justify-center gap-4 mb-10 text-xs font-semibold">
        <div className={`flex items-center gap-2 ${step === "form" ? "text-cyan-400" : "text-slate-400"}`}>
          <span className={`w-6 h-6 rounded-full flex items-center justify-center ${step === "form" ? "bg-cyan-500 text-slate-950 font-bold" : "bg-slate-800 text-slate-300"}`}>
            1
          </span>
          <span>Target Scope &amp; Info</span>
        </div>
        <span className="text-slate-600">—</span>
        <div className={`flex items-center gap-2 ${step === "payment" ? "text-cyan-400" : "text-slate-400"}`}>
          <span className={`w-6 h-6 rounded-full flex items-center justify-center ${step === "payment" ? "bg-cyan-500 text-slate-950 font-bold" : "bg-slate-800 text-slate-300"}`}>
            2
          </span>
          <span>Payment (₹1,999)</span>
        </div>
        <span className="text-slate-600">—</span>
        <div className={`flex items-center gap-2 ${step === "success" ? "text-emerald-400" : "text-slate-400"}`}>
          <span className={`w-6 h-6 rounded-full flex items-center justify-center ${step === "success" ? "bg-emerald-500 text-slate-950 font-bold" : "bg-slate-800 text-slate-300"}`}>
            3
          </span>
          <span>Confirmed</span>
        </div>
      </div>

      {/* STEP 1: Intake Form */}
      {step === "form" && (
        <div className="glass-panel rounded-2xl p-6 sm:p-10 border border-slate-800 shadow-2xl">
          <form onSubmit={handleFormSubmit} className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Target Domain */}
              <div className="sm:col-span-2 space-y-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-cyan-400" />
                  Target Website URL / Domain <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. https://mycompany.com or mysite.in"
                  value={targetUrl}
                  onChange={(e) => setTargetUrl(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400"
                  required
                />
              </div>

              {/* Contact Name */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5 text-cyan-400" />
                  Your Full Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  placeholder="Alex Sharma"
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400"
                  required
                />
              </div>

              {/* Contact Email */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5 text-cyan-400" />
                  Work Email <span className="text-red-400">*</span>
                </label>
                <input
                  type="email"
                  placeholder="alex@company.com"
                  value={contactEmail}
                  onChange={(e) => setContactEmail(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400"
                  required
                />
              </div>

              {/* Organization */}
              <div className="sm:col-span-2 space-y-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Building className="w-3.5 h-3.5 text-slate-400" />
                  Organization / Startup Name (Optional)
                </label>
                <input
                  type="text"
                  placeholder="Acme Tech Pvt Ltd"
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400"
                />
              </div>

              {/* Scope Notes */}
              <div className="sm:col-span-2 space-y-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Specific Scope or Concerns (Optional)
                </label>
                <textarea
                  rows={3}
                  placeholder="e.g. Focus on our customer dashboard, API headers, or recent domain migration."
                  value={scopeNotes}
                  onChange={(e) => setScopeNotes(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400"
                />
              </div>
            </div>

            {/* Authorization Affirmation */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  id="intake-auth-check"
                  checked={authorized}
                  onChange={(e) => setAuthorized(e.target.checked)}
                  className="mt-1 rounded border-slate-700 text-cyan-500 focus:ring-0"
                />
                <label htmlFor="intake-auth-check" className="text-xs text-slate-300 leading-relaxed cursor-pointer">
                  <strong>Legal Authorization Affirmation:</strong> I certify that I am the owner or authorized representative of the target domain specified above. I explicitly authorize AegisScan security engineers to conduct non-invasive security assessments.
                </label>
              </div>
            </div>

            {error && (
              <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-400 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 font-bold text-sm hover:brightness-110 flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 transition disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                  <span>Preparing Order...</span>
                </>
              ) : (
                <>
                  <span>Continue to Payment (₹1,999)</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>
      )}

      {/* STEP 2: Payment Simulation */}
      {step === "payment" && createdAudit && (
        <div className="glass-panel rounded-2xl p-6 sm:p-10 border border-slate-800 shadow-2xl space-y-6">
          <div className="border-b border-slate-800 pb-6">
            <h3 className="text-xl font-bold text-white">Order Summary</h3>
            <p className="text-xs text-slate-400 mt-1">Review your security assessment order details</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Target Domain:</span>
              <span className="font-mono text-slate-200 font-semibold">{createdAudit.target_url}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Contact:</span>
              <span className="text-slate-200">{createdAudit.contact_name} ({createdAudit.contact_email})</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Service:</span>
              <span className="text-slate-200">Advanced Website Security Audit + 1 Retest</span>
            </div>
            <div className="border-t border-slate-800 pt-3 flex justify-between text-sm font-bold text-white">
              <span>Total Amount:</span>
              <span className="text-cyan-400 font-mono">₹1,999.00</span>
            </div>
          </div>

          {/* Payment Method Selector */}
          <div className="space-y-3">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
              Choose Payment Method
            </label>
            <div className="grid grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => setPaymentMethod("upi")}
                className={`p-3 rounded-xl border text-center text-xs font-semibold transition ${
                  paymentMethod === "upi"
                    ? "border-cyan-400 bg-cyan-950/20 text-cyan-400"
                    : "border-slate-800 bg-slate-900 text-slate-400 hover:text-slate-200"
                }`}
              >
                UPI (GPay, PhonePe, Paytm)
              </button>
              <button
                type="button"
                onClick={() => setPaymentMethod("card")}
                className={`p-3 rounded-xl border text-center text-xs font-semibold transition ${
                  paymentMethod === "card"
                    ? "border-cyan-400 bg-cyan-950/20 text-cyan-400"
                    : "border-slate-800 bg-slate-900 text-slate-400 hover:text-slate-200"
                }`}
              >
                Credit / Debit Card
              </button>
              <button
                type="button"
                onClick={() => setPaymentMethod("netbanking")}
                className={`p-3 rounded-xl border text-center text-xs font-semibold transition ${
                  paymentMethod === "netbanking"
                    ? "border-cyan-400 bg-cyan-950/20 text-cyan-400"
                    : "border-slate-800 bg-slate-900 text-slate-400 hover:text-slate-200"
                }`}
              >
                Net Banking
              </button>
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-400 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex gap-4">
            <button
              onClick={() => setStep("form")}
              disabled={paying}
              className="px-5 py-3 rounded-xl border border-slate-700 text-slate-300 text-xs font-semibold hover:border-slate-500 transition"
            >
              Back
            </button>
            <button
              onClick={handlePayment}
              disabled={paying}
              className="flex-1 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 font-bold text-sm hover:brightness-110 flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 transition disabled:opacity-50"
            >
              {paying ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                  <span>Processing Secure Payment...</span>
                </>
              ) : (
                <>
                  <CreditCard className="w-4 h-4" />
                  <span>Pay ₹1,999 &amp; Start Audit</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Order Confirmation */}
      {step === "success" && paymentReceipt && (
        <div className="glass-panel rounded-2xl p-8 sm:p-12 border border-slate-800 shadow-2xl text-center space-y-6">
          <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mx-auto">
            <CheckCircle className="w-8 h-8" />
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white">Payment Received &amp; Audit Initiated</h2>
            <p className="text-slate-400 text-xs sm:text-sm mt-1 max-w-md mx-auto">
              Thank you! Our security engineering team has received your assessment order and added it to the audit queue.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 max-w-md mx-auto text-left space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Transaction ID:</span>
              <span className="font-mono text-cyan-400">{paymentReceipt.transaction_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Amount Paid:</span>
              <span className="font-mono text-slate-200">₹{paymentReceipt.amount}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Status:</span>
              <span className="text-emerald-400 uppercase font-bold">{paymentReceipt.status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Estimated Turnaround:</span>
              <span className="text-slate-200">24 to 48 Hours</span>
            </div>
          </div>

          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/"
              className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-cyan-500 text-slate-950 font-semibold text-xs hover:brightness-110 transition"
            >
              Return to Homepage
            </Link>
            <Link
              href="/admin"
              className="w-full sm:w-auto px-6 py-2.5 rounded-xl border border-slate-700 text-slate-300 font-semibold text-xs hover:border-slate-500 transition"
            >
              View in Admin Dashboard
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
