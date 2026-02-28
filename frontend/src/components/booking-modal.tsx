"use client";

import { useState, useEffect } from "react";
import { MapPin, X, Phone, MessageCircle, Mail } from "lucide-react";
import type { ProviderWithPrices } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface BookingModalProps {
  provider: ProviderWithPrices;
  onClose: () => void;
}

export function BookingModal({ provider, onClose }: BookingModalProps) {
  const [firstname, setFirstname] = useState("");
  const [lastname, setLastname] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [service, setService] = useState("");
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [contactMethods, setContactMethods] = useState<any>(null);

  // Pre-fill from saved profile
  useEffect(() => {
    try {
      const raw = localStorage.getItem("rateright_profile");
      if (!raw) return;
      const p = JSON.parse(raw);
      if (p.firstname) setFirstname(p.firstname);
      if (p.lastname) setLastname(p.lastname);
      if (p.email) setEmail(p.email);
      if (p.phone) setPhone(p.phone);
    } catch {}
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("loading");
    try {
      const res = await fetch(`${API_URL}/api/book`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          firstname,
          lastname,
          email,
          phone,
          service,
          provider_name: provider.name,
          provider_phone: provider.phone,
          provider_email: provider.email,
          date: date || null,
          time: time || null,
        }),
      });
      if (!res.ok) throw new Error("Request failed");
      const data = await res.json();
      setContactMethods(data.contact_methods);
      setStatus("success");
    } catch {
      setStatus("error");
    }
  }

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="relative w-full max-w-md rounded-xl border border-border bg-background shadow-2xl overflow-hidden">
        <button
          onClick={onClose}
          className="absolute right-3 top-3 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-muted/80 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Header */}
        <div className="border-b border-border bg-muted/40 px-6 py-4 pr-12">
          <h2 className="text-base font-semibold leading-snug">
            Contact {provider.name}
          </h2>
          <p className="mt-1 flex items-start gap-1 text-[13px] leading-snug text-muted-foreground">
            <MapPin className="mt-0.5 h-3 w-3 shrink-0" />
            <span>{provider.address}</span>
          </p>
        </div>

        <div className="px-6 py-5">
          {status === "success" && contactMethods ? (
            <div className="space-y-4">
              <div className="rounded-lg bg-green-500/10 border border-green-500/30 px-4 py-3 text-center">
                <p className="text-sm font-semibold text-green-400">Contact details ready!</p>
                <p className="mt-1 text-[12px] text-muted-foreground">
                  Choose your preferred way to reach out
                </p>
              </div>

              {/* WhatsApp */}
              {contactMethods.whatsapp?.available && (
                <a
                  href={contactMethods.whatsapp.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 rounded-lg border border-green-500/30 bg-green-500/10 px-4 py-3 transition-colors hover:bg-green-500/20"
                >
                  <MessageCircle className="h-5 w-5 text-green-400" />
                  <div className="flex-1 text-left">
                    <p className="text-sm font-medium">WhatsApp</p>
                    <p className="text-[12px] text-muted-foreground">
                      {contactMethods.whatsapp.phone}
                    </p>
                  </div>
                </a>
              )}

              {/* Phone */}
              {contactMethods.phone?.available && (
                <a
                  href={`tel:${contactMethods.phone.number}`}
                  className="flex items-center gap-3 rounded-lg border border-blue-500/30 bg-blue-500/10 px-4 py-3 transition-colors hover:bg-blue-500/20"
                >
                  <Phone className="h-5 w-5 text-blue-400" />
                  <div className="flex-1 text-left">
                    <p className="text-sm font-medium">Call Now</p>
                    <p className="text-[12px] text-muted-foreground">
                      {contactMethods.phone.number}
                    </p>
                  </div>
                </a>
              )}

              {/* Email */}
              {contactMethods.email?.available && (
                <a
                  href={`mailto:${contactMethods.email.address}`}
                  className="flex items-center gap-3 rounded-lg border border-purple-500/30 bg-purple-500/10 px-4 py-3 transition-colors hover:bg-purple-500/20"
                >
                  <Mail className="h-5 w-5 text-purple-400" />
                  <div className="flex-1 text-left">
                    <p className="text-sm font-medium">Email</p>
                    <p className="text-[12px] text-muted-foreground">
                      {contactMethods.email.address}
                    </p>
                  </div>
                </a>
              )}

              <button
                onClick={onClose}
                className="w-full rounded-lg bg-muted px-4 py-2 text-sm font-medium transition-colors hover:bg-muted/80"
              >
                Close
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-[12px] font-medium text-muted-foreground">
                    First Name
                  </label>
                  <input
                    required
                    value={firstname}
                    onChange={(e) => setFirstname(e.target.value)}
                    className="w-full rounded-lg border border-border bg-muted px-3 py-2 text-[14px] focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-[12px] font-medium text-muted-foreground">
                    Last Name
                  </label>
                  <input
                    required
                    value={lastname}
                    onChange={(e) => setLastname(e.target.value)}
                    className="w-full rounded-lg border border-border bg-muted px-3 py-2 text-[14px] focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="mb-1 block text-[12px] font-medium text-muted-foreground">
                  Email
                </label>
                <input
                  required
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-border bg-muted px-3 py-2 text-[14px] focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="mb-1 block text-[12px] font-medium text-muted-foreground">
                  Phone
                </label>
                <input
                  required
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+91 XXXXX XXXXX"
                  className="w-full rounded-lg border border-border bg-muted px-3 py-2 text-[14px] focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="mb-1 block text-[12px] font-medium text-muted-foreground">
                  Service Required
                </label>
                <input
                  required
                  value={service}
                  onChange={(e) => setService(e.target.value)}
                  placeholder="e.g., Car AC repair, Phone screen replacement"
                  className="w-full rounded-lg border border-border bg-muted px-3 py-2 text-[14px] focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-[12px] font-medium text-muted-foreground">
                    Preferred Date (Optional)
                  </label>
                  <input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="w-full rounded-lg border border-border bg-muted px-3 py-2 text-[14px] focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-[12px] font-medium text-muted-foreground">
                    Preferred Time (Optional)
                  </label>
                  <input
                    type="time"
                    value={time}
                    onChange={(e) => setTime(e.target.value)}
                    className="w-full rounded-lg border border-border bg-muted px-3 py-2 text-[14px] focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              {status === "error" && (
                <p className="text-[13px] text-red-400">
                  Something went wrong. Please try again.
                </p>
              )}

              <button
                type="submit"
                disabled={status === "loading"}
                className="mt-1 w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {status === "loading" ? "Processing…" : "Get Contact Details"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
