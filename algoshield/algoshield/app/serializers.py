from rest_framework import serializers
from .models import Customer, Building, Appartment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email', 'password']
        extra_kwargs = {"password": {"write_only": True}}
    
    def create(self, validated_data):
        email = validated_data['email']
        try:
            user = User.objects.get(email=email)
            pass
        except:
            # username = email[:3] + str(random.randint(1000, 9999))
            username = validated_data['username']
            user = User(
                email=email,
                username=username
            )
            user.set_password(validated_data['password'])
            user.save()
            return user
        

    # def update(self, instance, validated_data):
    #     instance.email = validated_data.get('email', instance.email)
    #     if 'password' in validated_data:
    #         instance.set_password(validated_data['password'])
    #     instance.save()
    #     return instance


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ['user', 'name', 'account', 'gender', 'phone', 
            'address', 'display_image', 'is_owner']
        
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        customer = Customer.objects.create(user=user, **validated_data)
        return customer

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'owner', 'name', 'location', 'description', 'created_at']

class AppartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appartment
        fields = ['id', 'building', 'name', 'price', 'is_available', 'asset_id', 'description', 'created_at']
