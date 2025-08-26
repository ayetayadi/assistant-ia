import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';
import { SharedService } from './shared.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;

  constructor(private http: HttpClient, private sharedService: SharedService) {}

  private getHeaders(): HttpHeaders {
    const token = this.sharedService.getTokenFromCookie();
    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }


  register(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, data, {
      withCredentials: true
    });
  }

  login(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, data, {
      withCredentials: true
    });
  }

  getCurrentUser(): Observable<any> {
    return this.http.get(`${this.apiUrl}/me`, {
      headers: this.getHeaders(), withCredentials: true
    });
  }

forgotPassword(email: string) {
  return this.http.post<any>(`${this.apiUrl}/forgot-password`, { email });
}

resetPassword(token: string, newPassword: string) {
  return this.http.post<any>(`${this.apiUrl}/reset-password`, {
    token,
    new_password: newPassword
  });
}

  googleLoginRedirect(): void {
    const clientId = environment.googleClientId;
    const redirectUri = environment.googleRedirectUri;
    const scope = 'email profile';

    const url =
      `https://accounts.google.com/o/oauth2/v2/auth?response_type=code` +
      `&client_id=${clientId}` +
      `&redirect_uri=${redirectUri}` +
      `&scope=${scope}` +
      `&access_type=online&prompt=select_account`;

    window.location.href = url;
  }

}
