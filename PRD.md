# Bid Leveling Automation - V1 Architecture

## 1. System Overview

The V1 architecture represents a web-based bid leveling automation solution with real-time visualization, guided workflow, and high accuracy. The system automates the extraction of bid data from PDFs, performs intelligent leveling, and provides results in standardized Excel formats.

## 2. Core Components

### 2.1 Web Application

- **Frontend Framework**: React with Next.js
- **Backend Framework**: Django
- **User Authentication**: Basic email/password
- **File Upload**: Support for PDF bids and Excel templates
- **Embedded Spreadsheet**: Google Sheets iframe for real-time visualization
- **Chat Interface**: Chainlit or custom solution for streaming LLM responses

### 2.2 Agent Framework

- **OpenAI Assistant SDK**: Core agent capabilities with function calling
- *(MCP)** or direct API use: For Google Sheets API integration

### 2.3 Google Sheets Integration

- **Auth**: let user connect with Google account to create new spreadsheets and use API
- **API Connectivity**: Direct manipulation of spreadsheet data
- **Real-time Updates**: Visual progress tracking as leveling occurs (Sheet embedded into the front end)
- **Interactive Editing**: User can make corrections during the process
- **Template Support**: Working with user-provided spreadsheet formats

### 2.4 Validation Pipeline

- **Accuracy Metrics**: Quantitative measurement of leveling precision
- **Gap Analysis**: Identification of missing information across bids
- **Correction Mechanisms**: Automated and human-guided error correction
- **Performance Analytics**: Tracking system efficiency and accuracy over time

### 2.5 Export Service

- **Excel Generation**: Converting leveled data into downloadable spreadsheets
- **Format Preservation**: Maintaining user template styles and formulas

## 3. Technical Stack

### 3.1 Frontend

- **Framework**: React.js with Next.js
- **UI Components**: Material-UI or similar component library
- **State Management**: Redux or Context API
- **Chat Interface**: Chainlit for streaming or custom solution

### 3.2 Backend

- **Server**: Django
- **Authentication**: Basic email/password system
- **File Handling**: Django file upload handlers
- **API Gateway**: For LLM and external service communication

### 3.3 External Services

- **LLM Provider**: OpenAI API (GPT-4) or Anthropic API (Claude)
- **Spreadsheet Service**: Google Sheets API
- **Storage**: No persistent document storage in V1

### 3.4 Database

- **User Data**: Django default database (PostgreSQL recommended)
- **Session Management**: Django session management

### 3.5 Deployment

- **Infrastructure**: Render
- **Containerization**: None initially
- **CI/CD**: None initially
- **Monitoring**: Basic performance tracking

## 5. Implementation Priorities

The goal is to derisk early one the complex parts of the pipeline.

1. **Basic Infrastructure Setup**: Web app deployed with placeholders in front and sample API. 

2. *Agent integration** : Basic chat agent available in front end

3. *Google Sheets Integration**: Embedding and API connectivity

4. **Document Processing Pipeline**: PDF upload extraction and structured data conversion

5. **Agent Implementation**: LLM-based automation for bid leveling

6. **Export Functionality**: Excel generation with format preservation

7. **Validation System**: Accuracy measurement and reporting

1. *Auth** and version management

## 6. Limitations & Future Expansion

### 6.1 V1 Limitations

- Limited to PDF and Excel input formats
- Basic template recognition capabilities
- No integration with external construction systems
- Limited offline functionality

### 6.2 Expansion for V2

- Enhanced extraction for complex bid structures
- Incremental leveling from existing worksheets
- Integration with Procore, Email systems
- Format preservation for custom templates

### 6.3 Expansion for V3

- Browser-use capabilities for non-API applications
- Advanced offline support considerations
- More sophisticated validation algorithms
- Enhanced interoperability with construction software ecosystem