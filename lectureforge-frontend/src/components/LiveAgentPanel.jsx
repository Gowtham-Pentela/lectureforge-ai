import React, { useMemo, useRef, useState } from "react";
import {
  Bot,
  CheckCircle2,
  Loader2,
  Mic,
  MicOff,
  MonitorUp,
  Send,
  Square,
} from "lucide-react";
import { askLiveAgent } from "../lib/api";

export default function LiveAgentPanel({
  jobId,
  studyKit,
  activeTab,
  selectedLanguage,
}) {
  const [messages, setMessages] = useState([
    {
      role: "agent",
      content:
        "I can follow the lecture context, listen through voice input, and stay aware when you share your screen.",
    },
  ]);
  const [draft, setDraft] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [screenShared, setScreenShared] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState("");
  const [screenStatus, setScreenStatus] = useState("");
  const [contextCards, setContextCards] = useState([]);
  const [error, setError] = useState("");
  const recognitionRef = useRef(null);
  const screenStreamRef = useRef(null);
  const screenVideoRef = useRef(null);
  const finalTranscriptRef = useRef("");
  const manuallyStoppedVoiceRef = useRef(false);

  const quickPrompts = useMemo(
    () => [
      "Explain the current chapter in plain English.",
      "Quiz me on the most important concept.",
      "What should I focus on next?",
    ],
    []
  );

  async function handleSubmit(event, overrideMessage) {
    event?.preventDefault();

    const message = (overrideMessage || draft).trim();

    if (!message || isAsking) {
      return;
    }

    const userMessage = { role: "user", content: message };
    setMessages((previous) => [...previous, userMessage]);
    setDraft("");
    setIsAsking(true);
    setError("");

    try {
      const response = await askLiveAgent({
        jobId,
        message,
        activeTab,
        targetLanguage: selectedLanguage,
        screenShared,
        voiceEnabled: isListening,
      });

      setContextCards(response.context_cards || []);
      setMessages((previous) => [
        ...previous,
        { role: "agent", content: response.reply },
      ]);
    } catch (err) {
      setError(err.message || "Live agent failed");
      setMessages((previous) => [
        ...previous,
        {
          role: "agent",
          content:
            "I could not reach the live agent service. The voice and screen controls are still ready when the backend is available.",
        },
      ]);
    } finally {
      setIsAsking(false);
    }
  }

  function toggleVoice() {
    if (isListening) {
      manuallyStoppedVoiceRef.current = true;
      recognitionRef.current?.stop();
      setIsListening(false);
      setVoiceStatus("Voice stopped.");
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setError(
        "Voice input is not supported in this browser. Chrome or Edge usually work best."
      );
      return;
    }

    finalTranscriptRef.current = "";
    manuallyStoppedVoiceRef.current = false;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = getRecognitionLanguage(selectedLanguage);

    recognition.onresult = (event) => {
      let finalTranscript = "";
      let interimTranscript = "";

      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        const text = result[0]?.transcript || "";

        if (result.isFinal) {
          finalTranscript += text;
        } else {
          interimTranscript += text;
        }
      }

      const nextTranscript = `${finalTranscriptRef.current} ${finalTranscript}`.trim();

      if (finalTranscript) {
        finalTranscriptRef.current = nextTranscript;
        setDraft(nextTranscript);
        setVoiceStatus("Captured voice input. Press send or keep speaking.");
        return;
      }

      if (interimTranscript) {
        const preview = `${finalTranscriptRef.current} ${interimTranscript}`.trim();
        setDraft(preview);
        setVoiceStatus("Listening...");
      }
    };

    recognition.onerror = (event) => {
      const message = getSpeechErrorMessage(event.error);
      setError(message);
      setVoiceStatus(message);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);

      if (finalTranscriptRef.current.trim()) {
        setVoiceStatus("Voice captured. Press send when ready.");
        return;
      }

      if (manuallyStoppedVoiceRef.current) {
        return;
      }

      setVoiceStatus(
        "No voice was captured. Check microphone permission, then try speaking after the button turns blue."
      );
    };

    recognitionRef.current = recognition;
    setError("");
    setVoiceStatus("Requesting microphone permission...");

    try {
      recognition.start();
      setIsListening(true);
      setVoiceStatus("Listening...");
    } catch (err) {
      setIsListening(false);
      setError(err.message || "Could not start voice input.");
      setVoiceStatus("");
    }
  }

  async function toggleScreenShare() {
    if (screenShared) {
      stopScreenShare();
      return;
    }

    if (!navigator.mediaDevices?.getDisplayMedia) {
      setError("Screen sharing is not supported in this browser.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: false,
      });

      screenStreamRef.current = stream;
      setScreenShared(true);
      setScreenStatus("Screen sharing active.");
      setError("");

      if (screenVideoRef.current) {
        screenVideoRef.current.srcObject = stream;
      }

      stream.getVideoTracks()[0].addEventListener("ended", () => {
        setScreenShared(false);
        screenStreamRef.current = null;
        setScreenStatus("Screen sharing stopped.");

        if (screenVideoRef.current) {
          screenVideoRef.current.srcObject = null;
        }
      });
    } catch (err) {
      const message =
        err.name === "NotAllowedError"
          ? "Screen sharing permission was blocked or cancelled."
          : err.message || "Screen sharing was cancelled.";
      setError(message);
      setScreenStatus(message);
    }
  }

  function stopScreenShare() {
    screenStreamRef.current?.getTracks().forEach((track) => track.stop());
    screenStreamRef.current = null;
    setScreenShared(false);
    setScreenStatus("Screen sharing stopped.");

    if (screenVideoRef.current) {
      screenVideoRef.current.srcObject = null;
    }
  }

  return (
    <section className="grid gap-4 xl:grid-cols-[1fr_18rem]">
      <div className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)]">
        <div className="border-b border-[var(--app-border)] px-5 py-4">
          <p className="text-xs font-bold uppercase tracking-[0.24em] text-[var(--app-soft)]">
            Live AI agent
          </p>
          <h2 className="mt-2 font-serif text-2xl font-semibold text-[var(--app-text)]">
            Ask with voice or screen context
          </h2>
        </div>

        <div className="max-h-[480px] space-y-4 overflow-y-auto px-5 py-5">
          {messages.map((message, index) => (
            <article
              key={`${message.role}-${index}`}
              className={`max-w-[88%] rounded-md border px-4 py-3 text-sm leading-6 ${
                message.role === "user"
                  ? "ml-auto border-[var(--app-accent)] bg-[var(--app-accent-soft)] text-[var(--app-text)]"
                  : "border-[var(--app-border)] bg-[var(--app-panel-muted)] text-[var(--app-text)]"
              }`}
            >
              {message.content}
            </article>
          ))}

          {isAsking && (
            <div className="inline-flex items-center gap-2 rounded-md border border-[var(--app-border)] bg-[var(--app-panel-muted)] px-4 py-3 text-sm font-semibold text-[var(--app-muted)]">
              <Loader2 className="h-4 w-4 animate-spin" />
              Thinking with lecture context
            </div>
          )}
        </div>

        <form
          onSubmit={handleSubmit}
          className="border-t border-[var(--app-border)] px-5 py-4"
        >
          <div className="mb-3 flex flex-wrap gap-2">
            {quickPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => handleSubmit(null, prompt)}
                className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] px-3 py-1.5 text-xs font-semibold text-[var(--app-muted)] transition hover:bg-[var(--app-panel-muted)]"
              >
                {prompt}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask about the lecture..."
              className="min-h-11 flex-1 rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] px-3 text-sm text-[var(--app-text)] outline-none transition placeholder:text-[var(--app-soft)] focus:border-[var(--app-accent)] focus:ring-2 focus:ring-[var(--app-accent-soft)]"
            />

            <button
              type="submit"
              disabled={isAsking || !draft.trim()}
              className="grid h-11 w-11 place-items-center rounded-md bg-[var(--app-accent)] text-white transition hover:bg-[var(--app-accent-strong)] disabled:cursor-not-allowed disabled:bg-[var(--app-soft)]"
              aria-label="Send message"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </form>
      </div>

      <aside className="space-y-4">
        <div className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-4">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.22em] text-[var(--app-soft)]">
            Controls
          </p>

          <div className="grid gap-2">
            <button
              type="button"
              onClick={toggleVoice}
              className={`inline-flex items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-bold transition ${
                isListening
                  ? "bg-[var(--app-accent)] text-white"
                  : "border border-[var(--app-border)] bg-[var(--app-panel)] text-[var(--app-muted)] hover:bg-[var(--app-panel-muted)]"
              }`}
            >
              {isListening ? (
                <MicOff className="h-4 w-4" />
              ) : (
                <Mic className="h-4 w-4" />
              )}
              {isListening ? "Stop voice" : "Voice"}
            </button>

            <button
              type="button"
              onClick={toggleScreenShare}
              className={`inline-flex items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-bold transition ${
                screenShared
                  ? "bg-[var(--app-accent)] text-white"
                  : "border border-[var(--app-border)] bg-[var(--app-panel)] text-[var(--app-muted)] hover:bg-[var(--app-panel-muted)]"
              }`}
            >
              {screenShared ? (
                <Square className="h-4 w-4" />
              ) : (
                <MonitorUp className="h-4 w-4" />
              )}
              {screenShared ? "Stop share" : "Share screen"}
            </button>
          </div>

          {(voiceStatus || screenStatus) && (
            <div className="mt-3 space-y-2">
              {voiceStatus && (
                <p className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel-muted)] px-3 py-2 text-xs leading-5 text-[var(--app-muted)]">
                  {voiceStatus}
                </p>
              )}
              {screenStatus && (
                <p className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel-muted)] px-3 py-2 text-xs leading-5 text-[var(--app-muted)]">
                  {screenStatus}
                </p>
              )}
            </div>
          )}

          <div className="mt-3 overflow-hidden rounded-md border border-[var(--app-border)] bg-black">
            <video
              ref={screenVideoRef}
              autoPlay
              muted
              playsInline
              className={`aspect-video w-full object-cover ${
                screenShared ? "block" : "hidden"
              }`}
            />
            {!screenShared && (
              <div className="grid aspect-video place-items-center px-3 text-center text-xs font-semibold text-white/70">
                Share your screen to preview the active context.
              </div>
            )}
          </div>

          {screenShared && (
            <div className="mt-3 flex items-center gap-2 text-xs font-bold text-emerald-600">
              <CheckCircle2 className="h-4 w-4" />
              Screen context is attached to agent requests.
            </div>
          )}

          {error && (
            <p className="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs leading-5 text-red-700">
              {error}
            </p>
          )}
        </div>

        <div className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-4">
          <div className="mb-3 flex items-center gap-2 text-[var(--app-accent)]">
            <Bot className="h-4 w-4" />
            <p className="text-xs font-bold uppercase tracking-[0.22em]">
              Context
            </p>
          </div>

          <div className="space-y-2">
            {(contextCards.length
              ? contextCards
              : [
                  studyKit.lecture_title || "Generated study kit",
                  `Language: ${selectedLanguage}`,
                  `Active view: ${activeTab}`,
                  screenShared ? "Screen sharing active" : "Screen not shared",
                ]
            ).map((card) => (
              <div
                key={card}
                className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel-muted)] px-3 py-2 text-xs font-semibold leading-5 text-[var(--app-muted)]"
              >
                {card}
              </div>
            ))}
          </div>
        </div>
      </aside>
    </section>
  );
}

function getRecognitionLanguage(language) {
  const languageMap = {
    English: "en-US",
    Spanish: "es-ES",
    French: "fr-FR",
    Hindi: "hi-IN",
    Telugu: "te-IN",
    Arabic: "ar-SA",
    Urdu: "ur-PK",
  };

  return languageMap[language] || "en-US";
}

function getSpeechErrorMessage(errorCode) {
  const messages = {
    "not-allowed":
      "Microphone permission is blocked. Allow microphone access in the browser and try again.",
    "service-not-allowed":
      "The browser blocked speech recognition. Chrome or Edge usually work best.",
    "no-speech":
      "No speech was detected. Try again and start speaking after the button turns blue.",
    "audio-capture":
      "No microphone was found. Check your input device and browser permissions.",
    network:
      "Speech recognition needs browser speech services. Check network access or type your question.",
    aborted: "Voice input was stopped.",
  };

  return messages[errorCode] || "Voice input stopped before a message was captured.";
}
