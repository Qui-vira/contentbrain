"use client";

import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { FlutterwaveButton } from "./FlutterwaveButton";
import { BlockradarPayment } from "./BlockradarPayment";

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  serviceName: string;
  amount: number;
  currency?: string;
  calPaidUrl?: string;
}

export function PaymentModal({
  isOpen,
  onClose,
  serviceName,
  amount,
  currency = "USD",
  calPaidUrl,
}: PaymentModalProps) {
  const [tab, setTab] = useState<"fiat" | "crypto">("fiat");
  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState("");
  const [paymentStatus, setPaymentStatus] = useState<"idle" | "success">("idle");

  // Lock body scroll when open, reset state on close
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
      setTab("fiat");
      setEmail("");
      setEmailError("");
      setPaymentStatus("idle");
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  function validateEmail(): boolean {
    const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!valid) {
      setEmailError("A valid email is required for your receipt.");
      return false;
    }
    setEmailError("");
    return true;
  }

  function handleSuccess() {
    setPaymentStatus("success");
    if (calPaidUrl) {
      setTimeout(() => {
        window.open(calPaidUrl, "_blank");
        onClose();
      }, 2500);
    }
  }

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-md rounded-2xl border border-[#2a2a2a] bg-[#0d0d0d] p-6 shadow-2xl">
        {/* Header */}
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-widest text-[#666]">Complete your purchase</p>
            <h3 className="mt-1 text-base font-bold text-white">{serviceName}</h3>
            <p className="mt-1 text-3xl font-extrabold text-[#E63946]">
              ${amount.toLocaleString()}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 text-[#555] transition-colors hover:text-white cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {paymentStatus === "success" ? (
          /* Success state */
          <div className="py-8 text-center">
            <div className="mb-3 text-5xl">✓</div>
            <p className="text-lg font-bold text-green-400">Payment Confirmed!</p>
            <p className="mt-2 text-sm text-[#888]">
              {calPaidUrl
                ? "Opening your booking link in a moment..."
                : "Check your email for next steps."}
            </p>
          </div>
        ) : (
          <>
            {/* Email input */}
            <div className="mb-5">
              <label className="mb-1 block text-xs font-medium text-[#888]">
                Your Email <span className="text-[#555]">(for receipt + access)</span>
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setEmailError(""); }}
                placeholder="you@example.com"
                className="w-full rounded-lg border border-[#333] bg-[#1a1a1a] px-3 py-2 text-sm text-white placeholder:text-[#555] focus:border-[#E63946] focus:outline-none"
              />
              {emailError && (
                <p className="mt-1 text-xs text-red-400">{emailError}</p>
              )}
            </div>

            {/* Tab switcher */}
            <div className="mb-5 flex gap-2">
              <button
                type="button"
                onClick={() => setTab("fiat")}
                className={`flex-1 rounded-lg px-4 py-2 text-sm font-medium transition-colors cursor-pointer ${
                  tab === "fiat"
                    ? "bg-[#E63946] text-white"
                    : "bg-[#1a1a1a] text-[#888] hover:text-white"
                }`}
              >
                Card / Bank
              </button>
              <button
                type="button"
                onClick={() => setTab("crypto")}
                className={`flex-1 rounded-lg px-4 py-2 text-sm font-medium transition-colors cursor-pointer ${
                  tab === "crypto"
                    ? "bg-[#E63946] text-white"
                    : "bg-[#1a1a1a] text-[#888] hover:text-white"
                }`}
              >
                Crypto (USDC/BUSD)
              </button>
            </div>

            {/* Payment panel */}
            {tab === "fiat" ? (
              <FlutterwaveButton
                email={email}
                amount={amount}
                currency={currency}
                serviceName={serviceName}
                onValidate={validateEmail}
                onSuccess={handleSuccess}
              />
            ) : (
              <BlockradarPayment
                serviceName={serviceName}
                amount={amount}
                onSuccess={handleSuccess}
              />
            )}

            <p className="mt-4 text-center text-xs text-[#444]">
              Secured by Flutterwave &amp; Blockradar · 256-bit SSL
            </p>
          </>
        )}
      </div>
    </div>
  );
}
