# Social Skills Coach

A native mobile application built with React Native that helps adults improve their social skills through AI-powered conversation practice, real-time feedback, and progress tracking.

## Features

- **Conversation Practice**: Interactive AI-powered conversation simulations for various social scenarios
- **Real-time Feedback**: Get immediate feedback on your conversational skills
- **Progress Tracking**: Monitor your improvement over time with detailed analytics
- **Personalized Coaching**: Receive tailored recommendations based on your performance

## Tech Stack

- **Frontend**: React Native with Expo
- **State Management**: Redux with Redux Thunk
- **Backend**: Flask (Python)
- **AI/NLP**: OpenAI's GPT-3 for conversation simulation and TextBlob for feedback
- **Database**: PostgreSQL
- **Authentication**: JWT and OAuth (Google, Facebook)

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- npm or yarn
- Expo CLI

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/social-skills-coach.git
cd social-skills-coach
```

2. Install dependencies:
```
npm install
```

3. Start the development server:
```
npm start
```

4. Run on iOS or Android:
```
npm run ios
# or
npm run android
```

## Project Structure

```
social-skills-coach/
├── src/
│   ├── api/           # API services
│   ├── assets/        # Images, fonts, etc.
│   ├── components/    # Reusable components
│   ├── navigation/    # Navigation configuration
│   ├── redux/         # Redux state management
│   │   ├── actions/
│   │   ├── reducers/
│   ├── screens/       # App screens
│   ├── styles/        # Global styles
│   └── utils/         # Utility functions
├── App.js             # Entry point
└── package.json
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- OpenAI for providing the GPT API
- React Native community for the excellent framework
- All contributors who have helped shape this project 