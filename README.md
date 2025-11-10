# 🎙️ RecallOS - AI-Powered Audio Memory System

> Winner submission for Google Cloud Run Hackathon - AI Agents Category

## 🏆 What Makes RecallOS Special

RecallOS is the first audio memory system with **autonomous multi-agent coordination** and **cross-conversation pattern analysis**. Unlike traditional transcription services, RecallOS uses 4 AI agents that dynamically plan, negotiate, and execute tasks to provide intelligent insights across ALL your audio files.

### Novel Innovation: Cross-Conversation Insights

Our breakthrough feature analyzes patterns across multiple audio files to discover:
- Recurring topics and themes
- Speaker engagement patterns over time
- Decision evolution across conversations
- Timeline visualization of discussions

This goes beyond single-file analysis to provide meta-insights about your entire audio library.

## 🚀 Live Demo

- **UI**: [Your Vercel URL]
- **API**: https://recallos-api-490598019887.us-central1.run.app
- **Video Demo**: [YouTube link - create this next]

## 🏗️ Architecture

[Insert your Excalidraw diagram here]

### Google Cloud Services (7 total):
1. **Cloud Run** - Serverless deployment
2. **Google Speech-to-Text** - Transcription with speaker diarization
3. **Cloud Storage** - Audio file storage
4. **Firestore** - Session & metadata tracking
5. **Gemini 2.0 Flash** - Agent coordination & synthesis
6. **Google Embeddings** - Vector generation
7. **Google ADK** - Multi-agent framework

### AI Agents (4 total):
1. **Coordinator Agent** - Plans tasks & negotiates resources
2. **Transcription Agent** - Processes audio with Google Speech
3. **Memory Agent** - Stores & searches vector embeddings
4. **Insights Agent** - Cross-conversation pattern analysis (NOVEL)

## 🎯 Features

### 1. Intelligent Audio Processing
- Upload any audio format
- Google Speech-to-Text with speaker diarization
- Automatic storage in Cloud Storage
- Metadata tracking in Firestore

### 2. Autonomous Agent Queries
- Agents dynamically plan execution strategy
- Resource negotiation based on complexity
- Parallel or sequential execution
- Retry logic with exponential backoff

### 3. Cross-Conversation Insights (NOVEL)
- Analyze patterns across ALL uploaded files
- Speaker engagement analysis
- Topic evolution over time
- Actionable insights

## 🛠️ Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- TailwindCSS
- Vercel deployment

**Backend:**
- Python 3.12
- FastAPI
- Google ADK
- Pinecone Vector DB
- Cloud Run (2Gi memory, 300s timeout)

**AI/ML:**
- Google Gemini 2.0 Flash
- Google Speech-to-Text
- Google Embeddings (text-embedding-004)

## 📊 Technical Highlights

- **Production-grade error handling** with retry logic
- **Session tracking** across uploads and queries
- **Agent coordination** with planning and negotiation
- **Vector search** with semantic similarity
- **Speaker diarization** for multi-speaker audio
- **Scalable architecture** ready for production

## 🎬 Demo Video

[Embed YouTube video here - create next]

## 📝 How It Works

1. **Upload**: Audio → Cloud Storage → Google Speech → Firestore
2. **Query**: Coordinator plans → Agents execute → Synthesis responds
3. **Insights**: Cross-file analysis → Pattern detection → Actionable insights

## 🚀 Getting Started

[Add setup instructions]

## 🏅 Built For

Google Cloud Run Hackathon - AI Agents Category

Leveraging Google's Agent Development Kit, Cloud Run, and the full Google Cloud ecosystem to build an intelligent, scalable, production-ready application.

---

Made with ❤️ using Google Cloud
