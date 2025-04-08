import json
import logging
from django.core.management.base import BaseCommand
from tracker.models import User, Team, Activity, Leaderboard, Workout
from bson import ObjectId
from datetime import timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populate the database with test data for users, teams, activities, leaderboard, and workouts'

    def handle(self, *args, **kwargs):
        logger.debug('Starting database population...')
        
        # Clear existing data
        User.objects.all().delete()
        Team.objects.all().delete()
        Activity.objects.all().delete()
        Leaderboard.objects.all().delete()
        Workout.objects.all().delete()

        # Load test data from JSON file
        test_data_path = Path(__file__).resolve().parent.parent.parent.parent / 'octofit' / 'test_data.json'
        with open(test_data_path, 'r') as file:
            data = json.load(file)

        # Create users
        users = {}
        for user_data in data['users']:
            user = User.objects.create(
                _id=ObjectId(),
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )
            users[user_data['username']] = user
            logger.debug(f'Created user: {user}')

        # Create teams
        for team_data in data['teams']:
            team = Team.objects.create(
                _id=ObjectId(),
                name=team_data['name']
            )
            team.members.add(*[users[username] for username in team_data['members']])
            logger.debug(f'Created team: {team}')

        # Create activities
        for activity_data in data['activities']:
            activity = Activity.objects.create(
                _id=ObjectId(),
                user=users[activity_data['user']],
                activity_type=activity_data['activity_type'],
                duration=timedelta(hours=int(activity_data['duration'].split(':')[0]),
                                   minutes=int(activity_data['duration'].split(':')[1]))
            )
            logger.debug(f'Created activity: {activity}')

        # Create leaderboard entries
        for leaderboard_data in data['leaderboard']:
            leaderboard = Leaderboard.objects.create(
                _id=ObjectId(),
                user=users[leaderboard_data['user']],
                score=leaderboard_data['score']
            )
            logger.debug(f'Created leaderboard entry: {leaderboard}')

        # Create workouts
        for workout_data in data['workouts']:
            workout = Workout.objects.create(
                _id=ObjectId(),
                name=workout_data['name'],
                description=workout_data['description']
            )
            logger.debug(f'Created workout: {workout}')

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with test data.'))
