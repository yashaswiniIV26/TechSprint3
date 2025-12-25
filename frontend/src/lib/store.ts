import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  student_id: string;
  name: string;
  email: string;
  readiness_score: number;
  skills: string[];
  communication: string;
}

interface Profile {
  student_id: string;
  name: string;
  email: string;
  skills: string[];
  technical_skills: string[];
  soft_skills: string[];
  communication: string;
  job_interest: string[];
  preferred_roles: string[];
  coding_scores: Record<string, number>;
  aptitude_scores: Record<string, number>;
  academic_marks: Record<string, number>;
  readiness_score: number;
  resume_parsed: boolean;
}

interface AppState {
  user: User | null;
  profile: Profile | null;
  token: string | null;
  isLoading: boolean;
  
  setUser: (user: User | null) => void;
  setProfile: (profile: Profile | null) => void;
  setToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      profile: null,
      token: null,
      isLoading: false,
      
      setUser: (user) => set({ user }),
      setProfile: (profile) => set({ profile }),
      setToken: (token) => set({ token }),
      setLoading: (isLoading) => set({ isLoading }),
      logout: () => set({ user: null, profile: null, token: null }),
    }),
    {
      name: 'velionx-storage',
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
);
