# ZEBRAT TRADING - React Frontend

A modern, production-ready React frontend for the ZEBRAT TRADING educational stock trading simulator.

## 🚀 Features

- **Modern React 19** with TypeScript support
- **Tailwind CSS 4** with custom design system
- **React Hook Form** with Zod validation
- **React Router** for navigation
- **Axios** for API communication
- **Lucide React** for icons
- **Accessible** components with ARIA support
- **Responsive** design for all devices
- **Security** features (CSRF protection, secure cookies)

## 🎨 Design System

### Color Palette
- **Primary**: Green-based fintech colors (#12B97A, #0FA968, #1FCA90)
- **Base**: Neutral grays for text and backgrounds
- **Success**: Green for positive actions
- **Warning**: Amber for warnings
- **Danger**: Red for errors

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300-900
- **Fallbacks**: System fonts

## 🛠️ Setup & Installation

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:5000

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Environment Configuration:**
   Create a `.env` file in the root directory:
   ```env
   VITE_API_BASE_URL=http://localhost:5000
   VITE_APP_NAME=ZEBRAT TRADING
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

## 📁 Project Structure

```
src/
├── components/
│   ├── ui/                 # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── PasswordInput.tsx
│   │   ├── Checkbox.tsx
│   │   ├── Alert.tsx
│   │   └── Spinner.tsx
│   └── auth/              # Authentication components
│       └── PasswordStrengthBar.tsx
├── pages/
│   └── auth/              # Authentication pages
│       ├── Login.tsx
│       ├── SignUp.tsx
│       ├── ForgotPassword.tsx
│       └── ResetPassword.tsx
├── layouts/
│   └── AuthLayout.tsx     # Authentication layout
├── context/
│   └── AuthProvider.tsx   # Authentication context
├── lib/
│   ├── api.ts            # API client configuration
│   ├── utils.ts          # Utility functions
│   └── validation/
│       └── authSchemas.ts # Zod validation schemas
└── App.jsx               # Main app component
```

## 🔐 Authentication Features

### Login Page
- Email/username and password fields
- "Remember me" checkbox
- Forgot password link
- Demo account information
- OAuth integration (Google) - optional

### Sign Up Page
- Full name, email, password fields
- Optional username and referral code
- Real-time password strength indicator
- Terms and privacy policy agreement
- Email verification flow

### Password Reset
- Email-based password reset
- Secure token validation
- Password strength requirements
- Success/error states

## 🎯 API Integration

### Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/request-password-reset` - Request password reset
- `POST /api/auth/reset-password` - Reset password

### Security Features
- **CSRF Protection**: Automatic CSRF token handling
- **Secure Cookies**: HttpOnly, Secure, SameSite=Lax
- **Rate Limiting**: Built-in protection
- **Input Validation**: Client and server-side validation

## 🎨 UI Components

### Button Variants
- `primary` - Main action buttons (green)
- `secondary` - Secondary actions (outlined)
- `ghost` - Subtle actions (text only)
- `destructive` - Dangerous actions (red)

### Input Components
- `Input` - Standard text inputs
- `PasswordInput` - Password with show/hide toggle
- `Checkbox` - Custom styled checkboxes

### Feedback Components
- `Alert` - Success, error, warning, info messages
- `Spinner` - Loading indicators

## 📱 Responsive Design

- **Mobile-first** approach
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)
- **Grid layouts** for larger screens
- **Touch-friendly** interactions

## ♿ Accessibility

- **WCAG 2.1 AA** compliance
- **Keyboard navigation** support
- **Screen reader** friendly
- **Focus management**
- **ARIA labels** and descriptions
- **Color contrast** compliance

## 🧪 Testing

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Testing Strategy
- **Unit Tests**: Component logic and utilities
- **Integration Tests**: API integration and form validation
- **E2E Tests**: Complete user flows
- **Visual Tests**: Component snapshots

## 🔧 Configuration

### Environment Variables
```env
VITE_API_BASE_URL=http://localhost:5000  # Backend API URL
VITE_APP_NAME=ZEBRAT TRADING            # App name
VITE_APP_VERSION=1.0.0                  # App version
```

### Tailwind Configuration
- Custom color palette
- Inter font family
- Custom animations
- Responsive breakpoints

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Deployment Options
- **Static hosting** (Netlify, Vercel, GitHub Pages)
- **CDN** for global distribution
- **Docker** containerization
- **Cloud platforms** (AWS, GCP, Azure)

## 🔒 Security Considerations

- **No sensitive data** in localStorage
- **Secure cookie** handling
- **CSRF protection** on all forms
- **Input sanitization** and validation
- **XSS protection** with React
- **HTTPS** required in production

## 📊 Performance

- **Code splitting** with React.lazy
- **Tree shaking** for smaller bundles
- **Image optimization** with Vite
- **Lazy loading** for routes
- **Memoization** for expensive operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational purposes only. No real money or securities are involved.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review the code comments
3. Test with the demo account
4. Contact the development team

---

**ZEBRAT TRADING** - Learn, simulate, and build confidence in a risk-free environment.