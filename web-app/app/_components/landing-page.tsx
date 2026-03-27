"use client";

import {
  AlertCircle,
  ArrowRight,
  BarChart3,
  CheckCircle,
  Download,
  Eye,
  Lock,
  Shield,
  Target,
  Timer,
} from "lucide-react";
import Link from "next/link";

export default function LandingPage() {
  const macosDownloadHref =
    "https://github.com/Manit-J/AttentionAgent/releases/latest/download/ScreenGaze.dmg";

  return (
    <div className="space-y-16">
      <div className="text-center space-y-6 py-12">
        <div className="inline-flex items-center justify-center w-150 h-auto  dark:bg-blue-900/30 mb-4"></div>
        <h1 className="text-slate-900 dark:text-slate-50 text-5xl">
          Screen Gaze
        </h1>
        <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
          Track your screen gaze with a real-time machine learning model
        </p>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto pt-8">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-8 space-y-4">
            <h3 className="text-slate-900 dark:text-slate-50">
              Already have an account?
            </h3>
            <div className="flex flex-col gap-3">
              <Link
                href="/login"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors text-center"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 px-6 py-3 rounded-lg transition-colors text-center"
              >
                Register
              </Link>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-8 space-y-4">
            <h3 className="text-slate-900 dark:text-slate-50">
              Download the app
            </h3>
            <div className="flex flex-col gap-3">
              <a
                href={macosDownloadHref}
                download
                target="_blank"
                rel="noreferrer"
                className="bg-slate-800 hover:bg-slate-900 dark:bg-slate-700 dark:hover:bg-slate-600 text-white px-6 py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <Download className="w-5 h-5" />
                Download for macOS
              </a>
              <button className="bg-slate-800 hover:bg-slate-900 dark:bg-slate-700 dark:hover:bg-slate-600 text-white px-6 py-3 rounded-lg transition-colors flex items-center justify-center gap-2">
                <Download className="w-5 h-5" />
                Download for Windows
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-8 md:p-12">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 text-red-600 dark:text-red-400">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm uppercase tracking-wide">
                The Problem
              </span>
            </div>
            <h2 className="text-slate-900 dark:text-slate-50">
              Struggling to stay engaged with your screen?
            </h2>
            <div className="space-y-3 text-slate-600 dark:text-slate-400">
              <p>
                In today&apos;s world of constant notifications and
                distractions, maintaining engagement with your screen is harder
                than ever.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-1">•</span>
                  <span>
                    You lose track of how much time you actually spent working
                    on screen intensive task
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-1">•</span>
                  <span>
                    Distractions break your flow and productivity suffers
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-1">•</span>
                  <span>
                    You lack visibility into how engaged you are with your
                    screen and when you&apos;re most productive
                  </span>
                </li>
              </ul>
            </div>
          </div>

          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 text-green-600 dark:text-green-400">
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm uppercase tracking-wide">
                The Solution
              </span>
            </div>
            <h2 className="text-slate-900 dark:text-slate-50">
              Take control of your screen gaze.
            </h2>
            <div className="space-y-3 text-slate-600 dark:text-slate-400">
              <p>
                Screen Gaze brings your gaze back to your screen and the task
                you&apos;re trying to accomplish with real-time notifications.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span>
                    Track every gaze session with detailed metrics and scoring
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span>
                    Visualize your progress with a graph of your gaze quality
                    over time
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span>
                    Set daily goals for screen engagement and track your
                    progress
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-8">
        <div className="text-center">
          <h2 className="text-slate-900 dark:text-slate-50 mb-2 text-3xl">
            How it works
          </h2>
          <p className="text-slate-600 dark:text-slate-400">
            Simple workflow to help you stay engaged
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="relative">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                  <span className="text-blue-600 dark:text-blue-400">1</span>
                </div>
                <Target className="w-8 h-8 text-blue-600 dark:text-blue-400 opacity-20" />
              </div>
              <h3 className="text-slate-900 dark:text-slate-50">
                Set your session parameters
              </h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">
                Choose your session, short break, and long break durations for
                the task you want to work on.
              </p>
            </div>
            <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2 text-slate-300 dark:text-slate-700">
              <ArrowRight className="w-8 h-8" />
            </div>
          </div>

          <div className="relative">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                  <span className="text-purple-600 dark:text-purple-400">
                    2
                  </span>
                </div>
                <Timer className="w-8 h-8 text-purple-600 dark:text-purple-400 opacity-20" />
              </div>
              <h3 className="text-slate-900 dark:text-slate-50">
                Start Session
              </h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">
                Start your session and get to work. The app automatically tracks
                your screen gaze and notifies you when you look away.
              </p>
            </div>
            <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2 text-slate-300 dark:text-slate-700">
              <ArrowRight className="w-8 h-8" />
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                <span className="text-green-600 dark:text-green-400">3</span>
              </div>
              <BarChart3 className="w-8 h-8 text-green-600 dark:text-green-400 opacity-20" />
            </div>
            <h3 className="text-slate-900 dark:text-slate-50">
              Review & improve
            </h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Check out your progress and session results to see how you can
              improve your screen gaze.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/50 rounded-2xl p-8 md:p-12">
        <div className="text-center space-y-6 max-w-3xl mx-auto">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30">
            <Shield className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
          <h2 className="text-slate-900 dark:text-slate-50">
            Your privacy matters
          </h2>
          <p className="text-slate-600 dark:text-slate-400 text-lg">
            We&apos;re committed to protecting your data and respecting your
            privacy.
          </p>

          <div className="grid md:grid-cols-2 gap-6 pt-6">
            <div className="bg-white dark:bg-slate-900 rounded-lg p-6 space-y-2">
              <Lock className="w-8 h-8 text-blue-600 dark:text-blue-400 mx-auto" />
              <h3 className="text-slate-900 dark:text-slate-50">
                Non-Biomteric Data Only
              </h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">
                Biometric data is not collected. Only non-biometric data such as
                facial coordinates are collected to track your screen gaze.
              </p>
            </div>

            <div className="bg-white dark:bg-slate-900 rounded-lg p-6 space-y-2">
              <Eye className="w-8 h-8 text-blue-600 dark:text-blue-400 mx-auto" />
              <h3 className="text-slate-900 dark:text-slate-50">
                Secure Storage
              </h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">
                Data is stored securely on the cloud, only accessible by you.
              </p>
            </div>
          </div>
        </div>
      </div>

      <footer className="bg-blue-600 dark:bg-blue-700 rounded-lg py-6 -mx-6 md:-mx-8 lg:-mx-12 mt-16">
        <p className="text-center text-white">Download Screen Gaze today</p>
      </footer>
    </div>
  );
}
