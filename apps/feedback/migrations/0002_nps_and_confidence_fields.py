# Generated manually (the interactive makemigrations prompt for a
# one-off default doesn't work non-interactively). The defaults below
# are only used for the ALTER TABLE statement against any pre-existing
# rows (there are none in this project) — they are not carried forward
# as model-level defaults; new rows must set these explicitly, same as
# every other rating field on this model.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentfeedback',
            name='difficulty',
            field=models.PositiveSmallIntegerField(default=3, help_text='1 = Very Easy, 5 = Very Difficult'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studentfeedback',
            name='confidence_before',
            field=models.PositiveSmallIntegerField(
                default=3, help_text='1 = Not at all confident, 5 = Very confident'
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studentfeedback',
            name='confidence_after',
            field=models.PositiveSmallIntegerField(
                default=3, help_text='1 = Not at all confident, 5 = Very confident'
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studentfeedback',
            name='nps_score',
            field=models.PositiveSmallIntegerField(
                default=5,
                help_text='0-10: How likely are you to recommend this course to a friend or colleague?',
            ),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='studentfeedback',
            constraint=models.CheckConstraint(
                condition=models.Q(('difficulty__gte', 1), ('difficulty__lte', 5)), name='difficulty_1_to_5'
            ),
        ),
        migrations.AddConstraint(
            model_name='studentfeedback',
            constraint=models.CheckConstraint(
                condition=models.Q(('confidence_before__gte', 1), ('confidence_before__lte', 5)),
                name='confidence_before_1_to_5',
            ),
        ),
        migrations.AddConstraint(
            model_name='studentfeedback',
            constraint=models.CheckConstraint(
                condition=models.Q(('confidence_after__gte', 1), ('confidence_after__lte', 5)),
                name='confidence_after_1_to_5',
            ),
        ),
        migrations.AddConstraint(
            model_name='studentfeedback',
            constraint=models.CheckConstraint(
                condition=models.Q(('nps_score__gte', 0), ('nps_score__lte', 10)), name='nps_score_0_to_10'
            ),
        ),
    ]
