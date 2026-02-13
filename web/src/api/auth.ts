import { apiClient } from './axios';
import { User } from '../types';

export const fetchCurrentUser = async (): Promise<User> => {
    const { data } = await apiClient.get<User>('/api/v1/auth/me');
    return data;
};

export const logout = async (): Promise<void> => {
    await apiClient.post('/api/v1/auth/logout')
}