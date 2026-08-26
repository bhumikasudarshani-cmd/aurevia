import { create } from 'zustand';

// 1. Define the shape of the data (TypeScript interface)
interface AppState {
  cases: any[]; 
  notifications: any[];
  setCases: (cases: any[]) => void;
  updateCaseRisk: (caseId: string, newScore: number) => void;
  addLiveNotification: (notification: any) => void;
}

// 2. Create the actual global store
export const useStore = create<AppState>((set) => ({
  // --- Initial State ---
  cases: [],
  notifications: [],

  // --- Actions (Functions to update state) ---
  setCases: (cases) => set({ cases }),

  updateCaseRisk: (caseId, newScore) => 
    set((state) => ({
      cases: state.cases.map((c) => 
        c.id === caseId ? { ...c, riskScore: newScore } : c
      )
    })),

  addLiveNotification: (notification) =>
    set((state) => ({
      notifications: [notification, ...state.notifications]
    })),
}));