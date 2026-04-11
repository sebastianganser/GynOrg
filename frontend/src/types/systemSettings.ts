export interface SystemSettings {
    id: number;
    user_id: string;
    auto_logout_minutes: number;
    created_at: string;
    updated_at: string;
}

export interface SystemSettingsUpdate {
    auto_logout_minutes?: number;
}
