import { auth } from './app/auth';

export default auth((req) => {
  // req.auth has user's session
  // req.nextUrl is the URL they're trying to access
  
  // For now, we're not protecting any routes
  // When we add protected routes, we can add logic here
})

// See https://nextjs.org/docs/app/building-your-application/routing/middleware
export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
} 