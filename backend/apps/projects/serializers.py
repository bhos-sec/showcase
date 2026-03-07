"""
DRF serializers for the projects module.

Serializers define the public API representation of Project and
Language records, matching the shape expected by the React frontend.
"""

from rest_framework import serializers

from .models import Language, Project


class LanguageSerializer(serializers.ModelSerializer):
    """Serializes a programming language.

    Fields:
        name: Language name (e.g. "Python").
        color: Hex colour code (e.g. "#3572A5").
    """

    class Meta:
        model = Language
        fields = ["name", "color"]


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializes a project for the Forge list view.

    Matches the frontend contract::

        { id, name, description, stars, forks, languages: string[], status }

    The ``languages`` field is flattened to a list of name strings
    for compatibility with the existing React component.
    """

    languages = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "stars",
            "forks",
            "open_issues",
            "languages",
            "status",
            "github_url",
            "homepage_url",
        ]
