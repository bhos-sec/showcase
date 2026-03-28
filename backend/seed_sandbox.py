from apps.members.models import Badge, Member, MemberBadge, Tier

# Create exactly the badges requested in the user's screenshot
b_reviewer, _ = Badge.objects.get_or_create(
    name="Reviewer",
    defaults={"icon_name": "Reviewer", "description": "Code Review Specialist"},
)
b_architect, _ = Badge.objects.get_or_create(
    name="Architect",
    defaults={"icon_name": "Architect", "description": "System Architecture Expert"},
)
b_mentor, _ = Badge.objects.get_or_create(
    name="Mentor", defaults={"icon_name": "Mentor", "description": "Ecosystem Mentor"}
)

members = Member.objects.all().order_by("-score")

if members.exists():
    top_member = members[0]
    top_member.tier = Tier.FOUNDER
    top_member.save()
    MemberBadge.objects.get_or_create(member=top_member, badge=b_reviewer)
    MemberBadge.objects.get_or_create(member=top_member, badge=b_architect)

    if len(members) > 1:
        second_member = members[1]
        second_member.tier = Tier.LEAD
        second_member.save()
        MemberBadge.objects.get_or_create(member=second_member, badge=b_mentor)

    if len(members) > 2:
        third_member = members[2]
        third_member.tier = Tier.MENTOR
        third_member.save()
        MemberBadge.objects.get_or_create(member=third_member, badge=b_architect)

    for m in members[3:10]:
        m.tier = Tier.MEMBER
        m.save()
print("Successfully assigned tiers and badges to top sandbox members!")
