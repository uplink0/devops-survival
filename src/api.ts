export type User = { id:number; username:string; email:string; xp:number; streak:number; created_at:string };

const TOKEN_KEY='devops_survival_token';
export const token=()=>localStorage.getItem(TOKEN_KEY);
export const logout=()=>localStorage.removeItem(TOKEN_KEY);

async function request<T>(path:string, options:RequestInit={}) : Promise<T> {
  const headers = new Headers(options.headers);
  headers.set('Content-Type','application/json');
  const t=token(); if(t) headers.set('Authorization',`Bearer ${t}`);
  const res=await fetch(path,{...options,headers});
  const data=await res.json().catch(()=>({detail:'Server returned invalid JSON'}));
  if(!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

export async function register(username:string,email:string,password:string){
  const data=await request<{access_token:string;user:User}>('/api/auth/register',{method:'POST',body:JSON.stringify({username,email,password})});
  localStorage.setItem(TOKEN_KEY,data.access_token); return data.user;
}
export async function login(loginValue:string,password:string){
  const data=await request<{access_token:string;user:User}>('/api/auth/login',{method:'POST',body:JSON.stringify({login:loginValue,password})});
  localStorage.setItem(TOKEN_KEY,data.access_token); return data.user;
}
export const me=()=>request<User>('/api/auth/me');
export const profile=()=>request<{user:User;progress:{incident_id:string;solved:boolean;best_score:number;attempts:number;last_played:string}[]}>('/api/profile');
export const leaderboard=()=>request<{rank:number;username:string;xp:number;streak:number}[]>('/api/leaderboard');
export const saveProgress=(incident_id:string,solved:boolean,score:number)=>request('/api/progress',{method:'POST',body:JSON.stringify({incident_id,solved,score})});
