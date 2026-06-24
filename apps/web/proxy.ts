import { NextRequest, NextResponse } from "next/server";

const protectedPrefixes = ["/app", "/sign-in", "/onboarding"];

function shouldProtectPath(pathname: string) {
  if (process.env.DEMO_ACCESS_PROTECT_MARKETING === "true") {
    return true;
  }

  return protectedPrefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

function challenge(message = "FlowSight AI demo access required.") {
  return new NextResponse(message, {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="FlowSight AI Demo", charset="UTF-8"',
      "Cache-Control": "no-store"
    }
  });
}

function parseBasicAuth(header: string | null) {
  if (!header?.startsWith("Basic ")) {
    return null;
  }

  try {
    const decoded = atob(header.slice("Basic ".length).trim());
    const separatorIndex = decoded.indexOf(":");

    if (separatorIndex === -1) {
      return null;
    }

    return {
      username: decoded.slice(0, separatorIndex),
      password: decoded.slice(separatorIndex + 1)
    };
  } catch {
    return null;
  }
}

export function proxy(request: NextRequest) {
  const accessEnabled = process.env.DEMO_ACCESS_ENABLED === "true";

  if (!accessEnabled || !shouldProtectPath(request.nextUrl.pathname)) {
    return NextResponse.next();
  }

  const expectedUsername = process.env.DEMO_ACCESS_USERNAME;
  const expectedPassword = process.env.DEMO_ACCESS_PASSWORD;

  if (!expectedUsername || !expectedPassword) {
    return new NextResponse("FlowSight AI demo access is enabled but not configured.", {
      status: 503,
      headers: { "Cache-Control": "no-store" }
    });
  }

  const credentials = parseBasicAuth(request.headers.get("authorization"));

  if (credentials?.username === expectedUsername && credentials.password === expectedPassword) {
    return NextResponse.next();
  }

  return challenge();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};
