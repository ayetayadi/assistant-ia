import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { CookieService } from 'ngx-cookie-service';

@Injectable({
  providedIn: 'root'
})
export class SharedService {
  private tokenSubject = new BehaviorSubject<string | null>(null);
  private rememberMeSubject = new BehaviorSubject<boolean>(false);

  constructor(private cookieService: CookieService) {
    // Initialiser à partir des cookies au démarrage
    const storedToken = this.cookieService.get('auth_token');
    const rememberMe = this.cookieService.get('remember_me') === 'true';

    if (storedToken) {
      this.tokenSubject.next(storedToken);
    }

    this.rememberMeSubject.next(rememberMe);
  }

  /** Sauvegarde le token et remember_me dans les cookies */
  storeAuthInfo(token: string, rememberMe: boolean): void {
    const expirationTime = rememberMe ?       
       90 * 24 * 60 * 60 * 1000  // 3 months in milliseconds
      : 60 * 60 * 1000;  // 1 hour;

    // Cookies
    const expireDate = new Date(new Date().getTime() + expirationTime);
    const cookieOptions = {
      expires: expireDate,
      secure: true,
      sameSite: 'Strict' as 'Strict',
      path: '/'
    };

    this.cookieService.set('auth_token', token, cookieOptions);
    this.cookieService.set('remember_me', rememberMe.toString(), cookieOptions);

    // Memory
    this.tokenSubject.next(token);
    this.rememberMeSubject.next(rememberMe);
  }

  /** Supprime les cookies et le cache mémoire */
  clearAuthInfo(): void {
    this.cookieService.delete('auth_token', '/');
    this.cookieService.delete('remember_me', '/');
    this.tokenSubject.next(null);
    this.rememberMeSubject.next(false);
  }

  /** Récupère le token depuis le cache ou les cookies */
  getToken(): string | null {
    return this.cookieService.get('auth_token') || null;
  }

  /** Récupère le flag remember me */
  getRememberMe(): boolean {
    return this.rememberMeSubject.value || this.cookieService.get('remember_me') === 'true';
  }

  getTokenFromCookie(): string | null {
    const token = this.cookieService.get('auth_token');
    return token || null;
  }

  getRememberMeFromCookie(): boolean {
    return this.cookieService.get('remember_me') === 'true';
  }

  removeToken(): void {
    this.cookieService.delete('auth_token', '/');
    this.cookieService.delete('remember_me', '/');
    this.tokenSubject.next(null);
    this.rememberMeSubject.next(false);
  }
}

