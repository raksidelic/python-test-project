describe('Native Cypress Tests', () => {

    beforeEach(() => {
        // Native Cypress komutu. 
        cy.visit('/'); 
    });

    it('Should login successfully', () => {
        cy.get('#user-name').should('be.visible').clear().type('standard_user');
        cy.get('#password').clear().type('secret_sauce');
        cy.get('#login-button').click();

        // Assertion
        cy.url().should('include', '/inventory.html');
        cy.get('.title').should('have.text', 'Products');
    });

    it('Should fail intentionally (to check screenshot & allure)', () => {
        cy.get('#user-name').type('locked_out_user');
        cy.get('#password').type('wrong_password');
        cy.get('#login-button').click();

        // Assertion
        cy.get('[data-test="error"]').should('contain', 'Fail');
    });
});