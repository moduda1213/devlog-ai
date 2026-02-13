export interface User {
    id: string;          // UUID
    username: string;    // github_username
    github_id: number;   // github_user_id
    created_at: string;  // datetime
    avatar_url: string;
    selected_repo_id?: string;
    // email, avatar_url은 현재 백엔드 /me 엔드포인트에서 반환하지 않음
}

// server/app/schemas/repository.py -> GithubRepo (목록 조회용)
// server/app/schemas/repository.py -> RepositoryResponse (DB 저장된 것)
// 두 가지를 포괄하는 유연한 인터페이스
export interface Repository {
    id: string | number; // DB(UUID) 또는 GitHub(int) ID
    
    // 공통 필드
    name?: string;       // GithubRepo.name
    repo_name?: string;  // RepositoryResponse.repo_name (DB)
    full_name?: string;  // GithubRepo.full_name
    
    repo_url?: string;   // RepositoryResponse
    html_url?: string;   // GithubRepo
    
    is_selected: boolean;
    
    // GithubRepo에만 있는 필드 (선택 목록 표시용)
    private?: boolean;
    description?: string | null;
    language?: string; // 백엔드 스키마엔 없지만 목업 UI에 있어 일단 유지 (필요시 백엔드 추가)
    
    created_at?: string;
}

export interface Journal {
    id: string;          // UUID
    user_id: string;
    repository_id: string;
    date: string;        // YYYY-MM-DD
    
    summary: string;
    main_tasks: string[];
    learned_things: string[];

    commit_count: number;
    files_changed: number;
    lines_added: number;
    lines_deleted: number;

    created_at: string;
    updated_at: string;
}

export interface ApiResponse<T> {
    data: T;
    message?: string;
}