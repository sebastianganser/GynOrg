export interface JobPosition {
    id: number;
    name: string;
    description: string | null;
    active: boolean;
    created_at: string;
    updated_at: string | null;
}

export interface JobPositionCreate {
    name: string;
    description?: string;
    active?: boolean;
}

export interface JobPositionUpdate {
    name?: string;
    description?: string;
    active?: boolean;
}
