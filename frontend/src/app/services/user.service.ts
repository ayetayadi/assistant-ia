import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';
import { SharedService } from './shared.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = `${environment.apiUrl}/users`;

  constructor(
    private http: HttpClient,
    private sharedService: SharedService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.sharedService.getTokenFromCookie();
    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  
  getUserId(): Observable<any> {
    return this.http.get(`${this.apiUrl}/me`, {
      headers: this.getHeaders()
    });
  }

  getUserEmail(): Observable<any> {
    return this.http.get(`${this.apiUrl}/email`, {
      headers: this.getHeaders()
    });
  }

  getAllUsers(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl, {
      headers: this.getHeaders()
    });
  }

  updateUserEmail(userId: string, newEmail: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${userId}`, { email: newEmail }, {
      headers: this.getHeaders()
    });
  }

  deleteUser(userId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${userId}`, {
      headers: this.getHeaders()
    });
  }
}
