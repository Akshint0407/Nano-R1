const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Feedback = {
  id: string;
  rating: number;
  comment: string | null;
  created_at: string;
};

export type Message = {
  id: string;
  question: string;
  reasoning: string;
  answer: string;
  created_at: string;
  feedback: Feedback | null;
};

export type Conversation = {
  id: string;
  title: string;
  created_at: string;
};

export type ConversationDetail = Conversation & { messages: Message[] };

async function request<T>(
  path: string,
  accessToken: string | undefined,
  init?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Request to ${path} failed with ${res.status}`);
  }
  return res.json();
}

export const api = {
  register: (email: string, password: string) =>
    request<{ id: string; email: string }>("/auth/register", undefined, {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  listConversations: (accessToken: string) =>
    request<Conversation[]>("/conversations", accessToken),

  getConversation: (accessToken: string, id: string) =>
    request<ConversationDetail>(`/conversations/${id}`, accessToken),

  startConversation: (accessToken: string, question: string) =>
    request<ConversationDetail>("/conversations", accessToken, {
      method: "POST",
      body: JSON.stringify({ question }),
    }),

  addMessage: (accessToken: string, conversationId: string, question: string) =>
    request<Message>(`/conversations/${conversationId}/messages`, accessToken, {
      method: "POST",
      body: JSON.stringify({ question }),
    }),

  setFeedback: (accessToken: string, messageId: string, rating: 1 | -1, comment?: string) =>
    request<Feedback>(`/messages/${messageId}/feedback`, accessToken, {
      method: "PUT",
      body: JSON.stringify({ rating, comment }),
    }),
};
