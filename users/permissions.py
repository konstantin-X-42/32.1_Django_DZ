from rest_framework import permissions


class IsModer(permissions.BasePermission):
    # 31 задаем сообщение об ошибке при отказе в доступе
    message = 'Доступ разрешен только пользователям из группы модераторов.'

    def has_permission(self, request, view):
        # 31 проверяем, состоит ли текущий аутентифицированный пользователь в группе moders
        return request.user.groups.filter(name='moders').exists()


class IsOwner(permissions.BasePermission):
    # 31 задаем сообщение об ошибке при попытке доступа к чужому объекту
    message = 'Вы не являетесь владельцем данного объекта.'

    def has_object_permission(self, request, view, obj):
        # 31 проверяем, совпадает ли владелец объекта с текущим пользователем запроса
        return obj.owner == request.user


class IsCurrentUser(permissions.BasePermission):
    # 31 задаем сообщение об ошибке при попытке изменить или удалить чужой профиль
    message = 'Вы можете изменять или удалять только свой собственный профиль.'

    def has_object_permission(self, request, view, obj):
        # 31 проверяем, совпадает ли редактируемый профиль с текущим пользователем запроса
        return obj == request.user


#----до доп--

# from rest_framework import permissions
#
#
# class IsModer(permissions.BasePermission):
#     # 31 задаем сообщение об ошибке при отказе в доступе
#     message = 'Доступ разрешен только пользователям из группы модераторов.'
#
#     def has_permission(self, request, view):
#         # 31 проверяем, состоит ли текущий аутентифицированный пользователь в группе moders
#         return request.user.groups.filter(name='moders').exists()
#
#
# class IsOwner(permissions.BasePermission):
#     # 31 задаем сообщение об ошибке при попытке доступа к чужому объекту
#     message = 'Вы не являетесь владельцем данного объекта.'
#
#     def has_object_permission(self, request, view, obj):
#         # 31 проверяем, совпадает ли владелец объекта с текущим пользователем запроса
#         return obj.owner == request.user


#------31.2-----


# from rest_framework import permissions
#
#
# class IsModer(permissions.BasePermission):
#     # 31 задаем сообщение об ошибке при отказе в доступе
#     message = 'Доступ разрешен только пользователям из группы модераторов.'
#
#     def has_permission(self, request, view):
#         # 31 проверяем, состоит ли текущий аутентифицированный пользователь в группе moders
#         return request.user.groups.filter(name='moders').exists()
