Cypress.Commands.add('uploadSampleVideo', () => {
    cy.intercept('POST', '/upload', { fixture: 'response.json' }).as('upload');
    cy.get('input[type="file"]').selectFile('cypress/fixtures/test.mp4', { force: true });
    cy.wait('@upload');
});

const path = require('path');

describe('Video Summarization Tests', () => {
    beforeEach(() => {
        cy.visit('http://localhost:5000');
    });

    it('loads the homepage with upload UI', () => {
        cy.get('input[type="file"]').should('exist');
        cy.get('#fileButton').should('be.visible');
    });

    it('shows expanded details container after click', () => {
        cy.get('#transcriptionDetails').click();
        cy.get('#copyTranscription').should('be.visible');

        cy.get('#summaryDetails').click();
        cy.get('#copySummary').should('be.visible');
    });

    it('rejects invalid file', () => {
        cy.get('input[type="file"]').selectFile('cypress/fixtures/response.json', {force:true});
        cy.on('window:alert', (str) => {
          expect(str).to.equal('Please upload a valid video file.');
        });
    });

    it('shows loading state after upload', () => {
        cy.get('input[type="file"]').selectFile('cypress/fixtures/test.mp4', { force: true });
        cy.contains('Converting to mp3').should('be.visible');
        cy.get('.loader').should('be.visible');
    });

    it('shows results state after upload', () => {
        cy.uploadSampleVideo();

        cy.contains('Upload Complete').should('be.visible');
        cy.get('#summarizeButton').should('be.enabled');
    });

    it('displays relevant loading state after summarize button clicked', () => {
        let sendResponse

        const trigger = new Promise((resolve) => {
            sendResponse = resolve;
        });

        cy.intercept('POST', '/transcribe', (request) => {
            return trigger.then(() => {
                request.reply({ fixture: 'response.json' });
            });
        }).as('transcribe');

        cy.uploadSampleVideo();
        cy.get('#summarizeButton').click();
        cy.get('#loadingText').should('have.text', 'Transcribing audio');

        cy.then(() => {
            sendResponse();
        });

        cy.get('#loadingText').should('have.text', 'Summarizing into notes');
    });

    it('displays transcription and summary after processing', () => {
        cy.intercept('POST', '/transcribe', { fixture: 'response.json' }).as('transcribe');
        cy.intercept('POST', '/summarize', { fixture: 'response.json' }).as('summarize');

        cy.uploadSampleVideo();
        cy.get('#summarizeButton').click();

        cy.wait('@transcribe').its('response.statusCode').should('eq', 200);
        cy.wait('@summarize').its('response.statusCode').should('eq', 200);

        cy.get('#transcriptionDetails').click();
        cy.get('#summaryDetails').click();

        cy.get('#transcriptionText').should('have.text', 'This is a mocked transcription of the uploaded video.');
        cy.get('#summaryText').should('have.text', 'This is a mocked summary of the uploaded video.');
    });

    it('displays download state after processing', () => {
        cy.intercept('POST', '/transcribe', { fixture: 'response.json' }).as('transcribe');
        cy.intercept('POST', '/summarize', { fixture: 'response.json' }).as('summarize');

        cy.uploadSampleVideo();
        cy.get('#summarizeButton').click();

        cy.wait('@transcribe').its('response.statusCode').should('eq', 200);
        cy.wait('@summarize').its('response.statusCode').should('eq', 200);

        cy.contains('Download').should('be.visible');
        cy.get('#downloadButton').should('be.enabled');
    });

    it('exports PDF after download button is clicked', () => {
        cy.intercept('POST', '/transcribe', { fixture: 'response.json' }).as('transcribe');
        cy.intercept('POST', '/summarize', { fixture: 'response.json' }).as('summarize');

        cy.uploadSampleVideo();
        cy.get('#summarizeButton').click();

        cy.wait('@transcribe').its('response.statusCode').should('eq', 200);
        cy.wait('@summarize').its('response.statusCode').should('eq', 200);

        cy.get('#downloadButton').click();
        const downloadsFolder = Cypress.config('downloadsFolder');
        const fileName = 'export.pdf';

        cy.readFile(path.join(downloadsFolder, fileName)).should('exist');
    });
});