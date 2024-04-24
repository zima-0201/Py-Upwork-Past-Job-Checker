require('dotenv').config();
const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const TelegramBot = require('node-telegram-bot-api');
const { TELEGRAM_TOKEN, UPWORK_USERNAME, UPWORK_PASSWORD, TELEGRAM_CHAT_ID } = process.env;

const bot = new TelegramBot(TELEGRAM_TOKEN);

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function loginToWebsite() {
    const browser = await puppeteer.launch({ headless: false, args: ['--no-sandbox'] });
    const page = await browser.newPage();
    try {
        await page.goto('https://www.upwork.com/ab/account-security/login', { waitUntil: 'networkidle2' });

        await page.type('#login_username', UPWORK_USERNAME);
        await page.click('#login_password_continue');
        await page.waitForSelector('#login_password', { visible: true });
        await page.type('#login_password', UPWORK_PASSWORD);
        await page.waitForSelector('#login_control_continue', { visible: true, timeout: 5000 });

        await page.click('#login_control_continue');
        await page.click('#login_control_continue');
        await page.click('#login_control_continue');
        await page.waitForNavigation({ waitUntil: 'networkidle2' });
        console.log('Login successful');
        return { browser, page };
    } catch (error) {
        console.error('Login failed:', error);
        await browser.close();
        throw error;
    }
}

async function scrapeProjects(page) {
    let attempt = 0;
    maxAttempts = 5;
    const page_index = 10; // Set the maximum number of retries

    for (i = page_index; i > 0; i--) {
        try {
            attempt++;
            await page.goto(`https://www.upwork.com/nx/search/jobs?amount=500-&category2_uid=531770282580668420,531770282580668419,531770282580668418&location=Americas,Antarctica,Asia,Europe,Oceania&page=${page_index}&payment_verified=1&per_page=50&sort=recency&t=0,1`, { waitUntil: 'networkidle2', timeout: 60000 });
            // Scrape the links
            const links = await page.evaluate(() => {
                // Find the container
                const container = document.querySelector('.card-list-container');
                // If the container exists, find all 'a' elements with class 'up-n-link'
                if (container) {
                    return Array.from(container.querySelectorAll('a.up-n-link')).map(link => link.href);
                }
                return []; // Return an empty array if the container does not exist
            });

            // Output the links
            console.log(links);

            // Iterate over each link and visit
            for (const link of links) {
                try {
                    console.log(`Navigating to ${link}`);
                    await page.goto(link, { waitUntil: 'networkidle2', timeout: 60000 });

                    // Write the current link to a file, overwriting the previous content
                    await fs.writeFile('current_link.txt', link, 'utf8');
                    console.log('The current link has been written to current_link.txt');

                    // Here you can add more actions you want to perform on each page
                    const html = await page.content();
                    // Write the HTML content to a file
                    await fs.writeFile('upwork_page.html', html, 'utf8');
                    console.log('The HTML file has been saved on attempt ' + attempt);
                } catch (error) {
                    console.error('Scraping failed on attempt ' + attempt + ':', error);
                    if (attempt >= maxAttempts) {
                        throw new Error("Max retries reached, scraping failed: " + error.message);
                    }
                    console.log('Retrying in 10 seconds...');
                    await sleep(10000); // Wait for 10 seconds before retrying
                }
            }
        } catch (error) {
            console.error('Scraping failed on attempt ' + attempt + ':', error);
            if (attempt >= maxAttempts) {
                throw new Error("Max retries reached, scraping failed: " + error.message);
            }
            console.log('Retrying in 10 seconds...');
            await sleep(10000); // Wait for 10 seconds before retrying
        }
    }
}


async function main() {
    try {
        const { browser, page } = await loginToWebsite();
        let count = 0;

        while (true) {
            await scrapeProjects(page);
            count++
            // Process the HTML or send a notification
            console.log(`New Project Scraped: Check your HTML file for details: ` + count);
            await sleep(1000); // Wait for 60 seconds before the next scrape
        }
    } catch (error) {
        console.error('Error in main:', error);
        if (browser) {
            await browser.close();
        }
    }
}

main();
