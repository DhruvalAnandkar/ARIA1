import React from "react";
import { Text } from "react-native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import HomeScreen from "../screens/home/HomeScreen";
import SignScreen from "../screens/sign/SignScreen";
import GuideScreen from "../screens/guide/GuideScreen";
import ProfileScreen from "../screens/profile/ProfileScreen";
import { colors } from "../constants/theme";
import type { MainTabParamList } from "./types";

const Tab = createBottomTabNavigator<MainTabParamList>();

export default function MainNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarStyle: {
          backgroundColor: colors.background,
          borderTopColor: colors.border,
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        headerStyle: { backgroundColor: colors.background },
        headerTintColor: colors.text,
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          tabBarIcon: ({ color }) => (
            <Text style={{ fontSize: 18, color }}>H</Text>
          ),
          title: "ARIA",
        }}
      />
      <Tab.Screen
        name="Sign"
        component={SignScreen}
        options={{
          tabBarIcon: ({ color }) => (
            <Text style={{ fontSize: 18, color }}>S</Text>
          ),
          title: "SIGN",
        }}
      />
      <Tab.Screen
        name="Guide"
        component={GuideScreen}
        options={{
          tabBarIcon: ({ color }) => (
            <Text style={{ fontSize: 18, color }}>G</Text>
          ),
          title: "GUIDE",
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarIcon: ({ color }) => (
            <Text style={{ fontSize: 18, color }}>P</Text>
          ),
          title: "Profile",
        }}
      />
    </Tab.Navigator>
  );
}
