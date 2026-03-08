import { NextResponse } from "next/server";

export function middleware(request) {
  const { pathname } = request.nextUrl;

  const roomRoutePattern = /^\/room\/([^/]+)/;
  const match = pathname.match(roomRoutePattern);

  if (!match) return NextResponse.next();

  const sessionToken = request.cookies.get("session_token")?.value;

  if (!sessionToken) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/room/:path*"],
};