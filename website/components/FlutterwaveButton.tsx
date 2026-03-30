"use client";

import { useEffect, useState } from "react";

declare global {
  interface Window {
    FlutterwaveCheckout: (config: Record<string, unknown>) => void;
  }
}

interface FlutterwaveButtonProps {
  email: string;
  amount: number;
  currency: string;
  serviceName: string;
  onValidate: () => boolean;
  onSuccess: () => void;
}

export function FlutterwaveButton({
  email,
  amount,
  currency,
  serviceName,
  onValidate,
  onSuccess,
}: FlutterwaveButtonProps) {
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined" && typeof window.FlutterwaveCheckout === "function") {
      setScriptLoaded(true);
      return;
    }
    const existing = document.querySelector('script[src="https://checkout.flutterwave.com/v3.js"]');
    if (existing) {
      existing.addEventListener("load", () => setScriptLoaded(true));
      return;
    }
    const script = document.createElement("script");
    script.src = "https://checkout.flutterwave.com/v3.js";
    script.async = true;
    script.onload = () => setScriptLoaded(true);
    document.head.appendChild(script);
  }, []);

  async function handlePay() {
    if (!onValidate()) return;
    if (!scriptLoaded) {
      setError("Payment system loading, please try again.");
      return;
    }

    const publicKey = process.env.NEXT_PUBLIC_FLW_PUBLIC_KEY;
    if (!publicKey) {
      setError("Card payments not yet configured. Contact us directly to pay.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      window.FlutterwaveCheckout({
        public_key: publicKey,
        tx_ref: `QV-${Date.now()}`,
        amount,
        currency,
        payment_options: "card,banktransfer,ussd",
        customer: {
          email,
          name: email.split("@")[0],
        },
        customizations: {
          title: "Quivira",
          description: serviceName,
          logo: "https://bigquivdigitals.com/logo.png",
        },
        callback: async (data: Record<string, unknown>) => {
          if (data.status === "successful") {
            try {
              const res = await fetch("/api/payment/flutterwave/verify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ transaction_id: data.transaction_id }),
              });
              const result = await res.json();
              if (result.success) {
                onSuccess();
              } else {
                setError("Payment verification failed. DM @Quivira_Ophir with your transaction ID: " + data.transaction_id);
              }
            } catch {
              setError("Verification error. DM @Quivira_Ophir with transaction ID: " + data.transaction_id);
            }
          } else {
            setError("Payment was not completed.");
          }
          setLoading(false);
        },
        onclose: () => setLoading(false),
      });
    } catch {
      setError("Payment failed to launch. Please try again.");
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      <button
        type="button"
        onClick={handlePay}
        disabled={loading}
        className="w-full rounded-xl bg-[#E63946] px-4 py-3 text-sm font-bold text-white transition-colors hover:bg-[#FF4D5A] disabled:opacity-60 cursor-pointer"
      >
        {loading ? "Processing..." : `Pay $${amount.toLocaleString()} with Card / Bank`}
      </button>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
