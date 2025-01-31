import json
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Avg
from django.contrib.auth.hashers import make_password
from backend.core.models import (
    User,
    Category,
    TimeUnit,
    Listing,
    ListingRate,
    ListingPhoto,
    ListingType,
    ListingLocation,
    Review,
    Offer,
    Transaction,
)


class UserSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "password",
            "phone_number",
            "avatar",
            "average_rating",
            "biography",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def get_average_rating(self, obj):
        # Get all reviews for received by this user and aggregate the average
        avg_rating = Review.objects.filter(user=obj).aggregate(Avg("rating"))[
            "rating__avg"
        ]
        return avg_rating if avg_rating is not None else 0

    def get_avatar(self, obj):
        if obj.avatar:
            return self.context["request"].build_absolute_uri(obj.avatar.url)
        return None

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserCreateSerializer(UserSerializer):
    avatar = (
        serializers.ImageField(
            max_length=1000000, allow_empty_file=False, use_url=False
        ),
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(UserCreateSerializer):
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta(UserSerializer.Meta):
        fields = fields = (
            "username",
            "password",
            "phone_number",
            "avatar",
            "biography",
            "new_password",
        )
        extra_kwargs = {
            **UserSerializer.Meta.extra_kwargs,
            "username": {"required": False},
            "biography": {"required": False},
            "password": {"required": False},
            "phone_number": {"required": False},
        }

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.password = (
            make_password(validated_data["new_password"])
            if validated_data.get("new_password")
            else instance.password
        )
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance


class ListingPhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ListingPhoto
        fields = ["image_url"]

    # This will return the a path to the image
    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image_url and hasattr(obj.image_url, "url"):
            return (
                request.build_absolute_uri(obj.image_url.url)
                if request
                else obj.image_url.url
            )
        return None


class ListingRateSerializer(serializers.ModelSerializer):
    time_unit = serializers.ChoiceField(choices=TimeUnit.choices)

    class Meta:
        model = ListingRate
        fields = ["time_unit", "rate"]


class ListingLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingLocation
        fields = ["latitude", "longitude", "query", "notes"]


class ListingSerializer(serializers.ModelSerializer):
    # the source = listingphoto_set tells django to look for the reverse
    # relationship from Listing -> ListingPhoto
    # i.e. for each Listing, get all ListingPhotos, then serialize it through
    # the ListingPhotoSerializer
    photos = ListingPhotoSerializer(
        many=True, read_only=True, source="listingphoto_set"
    )
    category = serializers.ChoiceField(choices=Category.choices)
    listing_type = serializers.ChoiceField(choices=ListingType.choices)
    rates = ListingRateSerializer(many=True, read_only=True)
    # Optionally required only
    locations = ListingLocationSerializer(many=True, required=False)

    class Meta:
        model = Listing
        fields = [
            "id",
            "created_at",
            "updated_at",
            "uploaded_by",
            "title",
            "description",
            "category",
            "listing_type",
            "photos",
            "locations",
            "rates",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_created_by(self, obj):
        user = User.objects.get(email=obj.uploaded_by)
        return user.username


# Specific serializer for POSTing a Listing
# then this will split into the listing and listing_photos table
class ListingCreateSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(
        child=serializers.ImageField(
            max_length=1000000, allow_empty_file=False, use_url=False
        ),
        write_only=True,
        required=True,  # This makes it easy for me for now
    )

    category = serializers.ChoiceField(choices=Category.choices)
    listing_type = serializers.ChoiceField(choices=ListingType.choices)
    locations = serializers.CharField()
    rates = serializers.CharField()

    class Meta:
        model = Listing
        fields = [
            "id",
            "created_at",
            "updated_at",
            "title",
            "description",
            "category",
            "listing_type",
            "photos",
            "locations",
            "rates",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        # Extract the photos from the validated data
        photos_data = validated_data.pop("photos", [])
        # Extract the rates from the validated data
        rates_data = validated_data.pop("rates", [])
        # Extract the location from the validated data
        location_data = validated_data.pop("locations", [])

        rates_data = json.loads(rates_data)
        location_data = json.loads(location_data)

        # Create the base Listing object
        listing = Listing.objects.create(**validated_data)

        # Create a listing photo for each object, then link the listing FK back to it
        for photo in photos_data:
            ListingPhoto.objects.create(listing=listing, image_url=photo)

        # Create listing rating for included rating
        for rate_data in rates_data:
            ListingRate.objects.create(
                listing=listing,
                time_unit=rate_data["time_unit"],
                rate=rate_data["rate"],
            )

        for location_data in location_data:
            ListingLocation.objects.create(
                listing=listing,
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
                query=location_data["query"],
                notes=location_data["notes"],
            )

        return listing


class ListingUpdateSerializer(ListingCreateSerializer):
    id = serializers.IntegerField(required=True)

    # Override the photo field to be optional
    photos = serializers.ListField(
        child=serializers.ImageField(
            max_length=1000000, allow_empty_file=False, use_url=False
        ),
        write_only=True,
        required=False,
    )

    locations = serializers.CharField()
    rates = serializers.CharField()

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.category = validated_data.get("category", instance.category)
        instance.listing_type = validated_data.get(
            "listing_type", instance.listing_type
        )
        instance.save()

        # Update the photos but not required
        photos_data = validated_data.get("photos", [])
        if photos_data:
            # Delete old photos
            instance.listingphoto_set.all().delete()
            # Add new photos
            for photo in photos_data:
                ListingPhoto.objects.create(listing=instance, image_url=photo)

        # Update the rates
        rates_data = validated_data.get("rates", [])
        rates_data = json.loads(rates_data)
        if rates_data:
            # Delete old rates
            instance.rates.all().delete()
            # Add new rates
            for rate_data in rates_data:
                ListingRate.objects.create(
                    listing=instance,
                    time_unit=rate_data["time_unit"],
                    rate=rate_data["rate"],
                )

        # Update the locations
        location_data = validated_data.get("locations", [])
        location_data = json.loads(location_data)
        if location_data:
            # Delete old rates
            instance.locations.all().delete()
            # Add new rates
            for location in location_data:
                ListingLocation.objects.create(
                    listing=instance,
                    latitude=location["latitude"],
                    longitude=location["longitude"],
                    query=location["query"],
                    notes=location["notes"],
                )

        return instance


# Serializer for get request
class OfferSerializer(serializers.ModelSerializer):
    offered_by = serializers.SerializerMethodField()
    listing = serializers.SerializerMethodField()
    status = serializers.ChoiceField(choices=Offer.STATUS_CHOICES, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    time_unit = serializers.ChoiceField(choices=TimeUnit.choices, read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "offered_by",
            "listing",
            "price",
            "status",
            "created_at",
            "scheduled_start",
            "scheduled_end",
            "time_unit",
            "time_delta",
        ]

    # For all offered_by, show the user detail that is offering
    def get_offered_by(self, obj):
        return {
            "id": obj.offered_by.id,
            "username": obj.offered_by.username,
            "email": obj.offered_by.email,
        }

    # Show the listing detail for the offer
    def get_listing(self, obj):
        return {
            "id": obj.listing.id,
            "title": obj.listing.title,
            "category": obj.listing.get_category_display(),
        }


# Serializer for post request
class OfferCreateSerializer(serializers.Serializer):
    offered_by = serializers.StringRelatedField()
    listing_id = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    scheduled_start = serializers.DateTimeField()
    scheduled_end = serializers.DateTimeField()
    time_unit = serializers.ChoiceField(choices=TimeUnit.choices)
    time_delta = serializers.IntegerField(min_value=1)

    def validate(self, data):
        if data["scheduled_end"] <= data["scheduled_start"]:
            raise serializers.ValidationError("End time must be after start time")
        return data

    # Check that they are not submitting junk listings
    def validate_listing_id(self, value):
        try:
            Listing.objects.get(id=value)
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Listing does not exist")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        listing = Listing.objects.get(id=validated_data["listing_id"])
        return Offer.objects.create(
            offered_by=user,
            listing=listing,
            price=validated_data["price"],
            scheduled_start=validated_data["scheduled_start"],
            scheduled_end=validated_data["scheduled_end"],
            time_unit=validated_data["time_unit"],
            time_delta=validated_data["time_delta"],
        )


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    # For data creation
    reviewer_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "reviewer",
            "user",
            "rating",
            "description",
            "created_at",
            "user_id",
            "reviewer_id",
        ]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        reviewer_id = validated_data.pop("reviewer_id")
        user_id = validated_data.pop("user_id")

        reviewer = User.objects.get(id=reviewer_id)
        user = User.objects.get(id=user_id)

        return Review.objects.create(reviewer=reviewer, user=user, **validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    offer = OfferSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    # For data creation
    user_id = serializers.IntegerField(write_only=True)
    offer_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user",
            "offer",
            "amount",
            "status",
            "status_display",
            "created_at",
            "updated_at",
            "payment_id",
            "user_id",
            "offer_id",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        offer_id = validated_data.pop("offer_id")

        user = User.objects.get(id=user_id)
        offer = Offer.objects.get(id=offer_id)

        transaction = Transaction.objects.create(
            user=user, offer=offer, **validated_data
        )

        # Set the offer to be paid afterwards
        offer.paid()

        return transaction


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        phone_number = data.get("phone_number")

        # case 1: both email and phone number are not found, return error message "Both email and phone number not found"
        if (
            not User.objects.filter(email=email).exists()
            and not User.objects.filter(phone_number=phone_number).exists()
        ):
            raise serializers.ValidationError("Both email and phone number not found")

        # case 2: email is found but phone number is not found, return error message "Phone number not found"
        if (
            User.objects.filter(email=email).exists()
            and not User.objects.filter(phone_number=phone_number).exists()
        ):
            raise serializers.ValidationError("Phone number not found")

        # case 3: email is not found but phone number is found, return error message "Email not found"
        if (
            not User.objects.filter(email=email).exists()
            and User.objects.filter(phone_number=phone_number).exists()
        ):
            raise serializers.ValidationError("Email not found")
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # First check if the email exists
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "No account found with this email address"}, code="no_account"
            )

        # If email exists but password is wrong
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"password": "Incorrect password"}, code="wrong_password"
            )

        # If both are correct, return the token
        data = super().validate(attrs)
        return data
