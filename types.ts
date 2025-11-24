
export enum GameStatus {
  IDLE = 'IDLE',
  LOADING = 'LOADING',
  ACTIVE = 'ACTIVE',
  ERROR = 'ERROR'
}

export interface Metric {
  name: string;
  value: number; // 0-100
  trend: 'up' | 'down' | 'stable';
  description?: string;
}

export interface TurnData {
  turnNumber: number;
  narrative: string;
  metrics: Metric[];
  status: 'ongoing' | 'victory' | 'defeat';
  suggestedActions: string[];
  imagePrompt?: string; 
}

export interface HistoryEntry {
  role: 'user' | 'model';
  text: string;
  metricsSnapshot?: Metric[];
}

export interface ScenarioConfig {
  clientName: string;
  rawContext: string;
  files: File[];
  opportunityType: string;
  mediaRole: string;
  digitalMaturity: string;
}

export interface StrategyAnalysis {
  challengeStatement_A: string;
  challengeStatement_B: string;
  rumeltDiagnosis: string;
  rumeltGuidingPolicy: string;
  culturalTension: string;
  marketOpportunity: string;
  consumerInsight: string;
  behavioralJustification: string;
  keyAssumptions: string[];
  relevantMentalModels: string[];
  interpretation_challenger: string;
  interpretation_consultive: string;
  interpretation_mixed: string;
}
