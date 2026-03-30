"use client";

import { useEffect, useState, useRef } from "react";
import { Copy, Check, Loader2 } from "lucide-react";

interface BlockradarPaymentProps {
  serviceName: string;
  amount: number;
  onSuccess: () => void;
}

interface PaymentAddress {
  address: string;
  qrCodeUrl: string;
  network: string;
  tokens: string[];
}

export function BlockradarPayment({ serviceName, amount, onSuccess }: BlockradarPaymentProps) {
  const [paymentData, setPaymentData] = useState<PaymentAddress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function createAddress() {
      try {
        const res = await fetch("/api/payment/blockradar/create", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ serviceName, amount }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to create payment address");
        if (cancelled) return;
        setPaymentData(data);
        startPolling(data.address);
      } catch (e: unknown) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load payment address.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    createAddress();
    return () => {
      cancelled = true;
      if (pollRef.current) clearInterval(pollRef.current);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [serviceName, amount]);

  function startPolling(address: string) {
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(
          `/api/payment/blockradar/create?address=${encodeURIComponent(address)}&check=true`
        );
        const data = await res.json();
        if (data.confirmed) {
          clearInterval(pollRef.current!);
          onSuccess();
        }
      } catch {
        // ignore transient poll errors
      }
    }, 10000);
  }

  async function copyAddress() {
    if (!paymentData?.address) return;
    await navigator.clipboard.writeText(paymentData.address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-[#E63946]" />
        <span className="ml-2 text-sm text-[#888]">Generating payment address...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-900 bg-red-950/30 p-4 space-y-1">
        <p className="text-sm text-red-400">{error}</p>
        <p className="text-xs text-[#666]">
          DM{" "}
          <a href="https://t.me/Quivira_Ophir" target="_blank" rel="noopener noreferrer" className="underline text-[#888]">
            @Quivira_Ophir
          </a>{" "}
          to arrange crypto payment directly.
        </p>
      </div>
    );
  }

  if (!paymentData) return null;

  return (
    <div className="space-y-4">
      {/* Network + token badges */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-[#F0B90B]/10 px-3 py-1 text-xs font-semibold text-[#F0B90B]">
          {paymentData.network}
        </span>
        {paymentData.tokens.map((t) => (
          <span key={t} className="rounded-full bg-[#2775CA]/10 px-3 py-1 text-xs font-semibold text-[#2775CA]">
            {t}
          </span>
        ))}
      </div>

      {/* QR Code */}
      <div className="flex justify-center">
        <img
          src={paymentData.qrCodeUrl}
          alt="Payment QR Code"
          className="h-40 w-40 rounded-xl border border-[#333] bg-white p-1"
        />
      </div>

      {/* Amount box */}
      <div className="rounded-lg bg-[#1a1a1a] px-4 py-3 text-center">
        <p className="text-xs text-[#666]">Send exactly</p>
        <p className="text-lg font-bold text-white">${amount.toLocaleString()} USDC</p>
      </div>

      {/* Address row */}
      <div className="flex items-center gap-2 rounded-lg bg-[#1a1a1a] px-3 py-2">
        <span className="flex-1 truncate font-mono text-xs text-[#ccc]">{paymentData.address}</span>
        <button
          type="button"
          onClick={copyAddress}
          className="shrink-0 text-[#666] transition-colors hover:text-white cursor-pointer"
        >
          {copied ? <Check className="h-4 w-4 text-green-400" /> : <Copy className="h-4 w-4" />}
        </button>
      </div>

      {/* Polling status */}
      <div className="flex items-center justify-center gap-2 text-sm text-[#666]">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span>Waiting for payment confirmation...</span>
      </div>

      <p className="text-center text-xs text-[#555]">
        Only send USDC or BUSD on BNB Chain. Other tokens or chains will result in permanent loss.
      </p>
    </div>
  );
}
