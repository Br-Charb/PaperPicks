# PaperPicks
Our team proposes a sports prediction platform that focuses on the National Football League (NFL). Using a virtual currency system (not real money), users will be able to make predictions based on statistics such as passing yards and touchdowns and their virtual balance will update accordingly whether or not their prediction falls above or below a specific threshold. 

There will be two types of users: members and administrators. Members can register and log in, create predictions using virtual currency, and see their prediction history. Administrators can do everything members can do along with other capabilities like managing users (such as suspending or banning accounts) and updating statistics and game results. A dynamic database will be implemented to store the aforementioned information in this paragraph. For frontend-backend-database communication, operations such as user registration, authentication, and managing virtual balances will be implemented. 

Common UI elements will be used to indicate important actions that users can do which include a login/signup screen for new user creation and logging in, user profile section, and prediction history. We plan to maintain a clean and minimalistic design by using a simple color scheme and visuals. 

## Team
- Product Manager - Benjamin Charbonneau
- Scrum Master - Ryan Qu
- Development Team Member - Matthew Nguyen
- Development Team Member - Joshua Chalar

## Tech Stack
- Frontend - React
- Backend - FastAPI
- Database - PostgreSQL

## Development Process
- `main` - deployed branch, always should be live and working
- `dev` - primary development branch, where changes live before they are deployed
- `feature/<name>` - branches for new changes, one branch per feature

For new features or changes, first a branch must be made off dev called `feature/<name>` or `fix/<name>`. Once that addition is complete, it will be merged back into `dev`. From there, when a new update is ready to go live, a PR will be made merging `dev` into `main`.
*note: PRs into main require approval from a seperate team member, force pushes to `main` are blocked*
