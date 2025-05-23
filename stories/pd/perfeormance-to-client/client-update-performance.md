What is the user story ?
As a user I should be able to see the performance on the ui 

Why should we implement this user story ?
We are currently displaying the prices and orders but we have no way of telling how the current stock is performance, this will allow us to see the actual profit made

Explain the high level implementation from the ui stands point?

Currently we are displaying on the client the current price of the stock and the orders, we now would like to see the performance of the stock 

We will also remove the orders from the UI for now, since this is a growing data we will remove it from the real time database and store it in the firebase database instead



What files do we need for context, What files do we need to modify, why and what exactly do we need to do?

The backend userstory - stories\pd\perfeormance-to-client\userstory.md
The backend implementation plan - stories\pd\perfeormance-to-client\implementation_plan.md
The backend checklist - stories\pd\perfeormance-to-client\client-update-performance.md

this is where we are currently showing the data - client\src\pages\Dashboard\index.tsx

And this is the dashboard folder - client\src\pages\Dashboard

We are already getting the live data in the service, let's update it now to show the performance and remove the orders list

Look over the additional files and ask me detailed questions to make sure we are on the same page 


For each of the questions ask make it a multiple choice questions with different options A - F different options and put them in order of recommendation from A to F (F being the least recommended)

uestion 1: How should the performance data be displayed in the UI?
Display performance data in a new section within the existing card, showing total, unrealized, and realized values with color-coding for positive/negative values
Replace the orders accordion with a performance accordion that expands to show detailed metrics
Add a simple line showing only the total performance value in the main card view
Create a separate performance tab for each stock card that users can toggle to
Display performance as a chart/graph visualization
Show performance metrics in a tooltip that appears on hover
Question 2: How should we style the performance data to make it visually clear to users?
Use color-coding (green for positive, red for negative) with clear positive/negative signs
Use separate up/down arrow icons beside each value
Use progress bars to visualize the performance values
Use simple text without special styling
Use percentage indicators alongside the actual values
Use mini sparkline charts next to each value
Question 3: Since we're removing the orders section, what additional information should we include alongside the performance data?
Add timestamp showing when performance was last calculated
Include aggregate portfolio performance at the top of the dashboard
Show percentage change since previous day/period
No additional information needed
Show a breakdown of performance by time periods (day, week, month)
Include performance ranking compared to other stocks in the portfolio

Answers:
Question 1 - Let's create a new TickerCard.Component.tx - client\src\pages\Dashboard\Component - We will remove the order section and we will brainstorm a new mobile friendly card that displays both the prices and the performance on the card directly, for now the card will not be clickable

Q2- 1

Q2 - 1, 2