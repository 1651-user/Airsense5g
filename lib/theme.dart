import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppSpacing {
  // Spacing values
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;

  // Edge insets shortcuts
  static const EdgeInsets paddingXs = EdgeInsets.all(xs);
  static const EdgeInsets paddingSm = EdgeInsets.all(sm);
  static const EdgeInsets paddingMd = EdgeInsets.all(md);
  static const EdgeInsets paddingLg = EdgeInsets.all(lg);
  static const EdgeInsets paddingXl = EdgeInsets.all(xl);

  // Horizontal padding
  static const EdgeInsets horizontalXs = EdgeInsets.symmetric(horizontal: xs);
  static const EdgeInsets horizontalSm = EdgeInsets.symmetric(horizontal: sm);
  static const EdgeInsets horizontalMd = EdgeInsets.symmetric(horizontal: md);
  static const EdgeInsets horizontalLg = EdgeInsets.symmetric(horizontal: lg);
  static const EdgeInsets horizontalXl = EdgeInsets.symmetric(horizontal: xl);

  // Vertical padding
  static const EdgeInsets verticalXs = EdgeInsets.symmetric(vertical: xs);
  static const EdgeInsets verticalSm = EdgeInsets.symmetric(vertical: sm);
  static const EdgeInsets verticalMd = EdgeInsets.symmetric(vertical: md);
  static const EdgeInsets verticalLg = EdgeInsets.symmetric(vertical: lg);
  static const EdgeInsets verticalXl = EdgeInsets.symmetric(vertical: xl);
}

/// Border radius constants for consistent rounded corners
class AppRadius {
  static const double sm = 8.0;
  static const double md = 12.0;
  static const double lg = 16.0;
  static const double xl = 24.0;
}

// =============================================================================
// TEXT STYLE EXTENSIONS
// =============================================================================

/// Extension to add text style utilities to BuildContext
/// Access via context.textStyles
extension TextStyleContext on BuildContext {
  TextTheme get textStyles => Theme.of(this).textTheme;
}

/// Helper methods for common text style modifications
extension TextStyleExtensions on TextStyle {
  /// Make text bold
  TextStyle get bold => copyWith(fontWeight: FontWeight.bold);

  /// Make text semi-bold
  TextStyle get semiBold => copyWith(fontWeight: FontWeight.w600);

  /// Make text medium weight
  TextStyle get medium => copyWith(fontWeight: FontWeight.w500);

  /// Make text normal weight
  TextStyle get normal => copyWith(fontWeight: FontWeight.w400);

  /// Make text light
  TextStyle get light => copyWith(fontWeight: FontWeight.w300);

  /// Add custom color
  TextStyle withColor(Color color) => copyWith(color: color);

  /// Add custom size
  TextStyle withSize(double size) => copyWith(fontSize: size);
}

// =============================================================================
// COLORS
// =============================================================================

/// Medical-themed color palette for light mode
class LightModeColors {
  // Primary: Medical Blue
  static const lightPrimary = Color(0xFF2196F3);
  static const lightOnPrimary = Color(0xFFFFFFFF);
  static const lightPrimaryContainer = Color(0xFFBBDEFB);
  static const lightOnPrimaryContainer = Color(0xFF0D47A1);

  // Secondary: Success Green
  static const lightSecondary = Color(0xFF43A047);
  static const lightOnSecondary = Color(0xFFFFFFFF);

  // Tertiary: Warning Orange
  static const lightTertiary = Color(0xFFFF9800);
  static const lightOnTertiary = Color(0xFFFFFFFF);

  // Error colors (Hazardous Red)
  static const lightError = Color(0xFFE53935);
  static const lightOnError = Color(0xFFFFFFFF);
  static const lightErrorContainer = Color(0xFFFFCDD2);
  static const lightOnErrorContainer = Color(0xFFB71C1C);

  // Surface and background: Clean medical aesthetic
  static const lightSurface = Color(0xFFFFFFFF);
  static const lightOnSurface = Color(0xFF212121);
  static const lightBackground = Color(0xFFF5F7FA);
  static const lightSurfaceVariant = Color(0xFFF0F4F8);
  static const lightOnSurfaceVariant = Color(0xFF546E7A);

  // Outline and shadow
  static const lightOutline = Color(0xFFBDBDBD);
  static const lightShadow = Color(0xFF000000);
  static const lightInversePrimary = Color(0xFF64B5F6);

  // AQI-specific colors
  static const aqiGood = Color(0xFF43A047);
  static const aqiModerate = Color(0xFFFF9800);
  static const aqiUnhealthy = Color(0xFFFF5722);
  static const aqiHazardous = Color(0xFFE53935);
}

/// Dark mode colors (Deep Violet/Black Theme with Red/Pink Accents)
class DarkModeColors {
  // Primary: Soft Violet/Purple
  static const darkPrimary =
      Color(0xFFD0BCFF); // Soft purple for icons/highlights
  static const darkOnPrimary = Color(0xFF381E72); // Dark purple
  static const darkPrimaryContainer = Color(0xFF4F378B);
  static const darkOnPrimaryContainer = Color(0xFFEADDFF);

  // Secondary: Pink/Red Accent
  static const darkSecondary = Color(0xFFFF2E63); // Vibrant Red/Pink
  static const darkOnSecondary = Color(0xFFFFFFFF);

  // Tertiary: Violet
  static const darkTertiary = Color(0xFF7B61FF);
  static const darkOnTertiary = Color(0xFFFFFFFF);

  // Error colors (Red/Pink for High Risk)
  static const darkError = Color(0xFFFF2E63); // Red/Pink
  static const darkOnError = Color(0xFFFFFFFF);
  static const darkErrorContainer =
      Color(0xFF2C1517); // Dark reddish background
  static const darkOnErrorContainer = Color(0xFFFFDAD6);

  // Surface and background: Deep Violet/Black
  static const darkSurface =
      Color(0xFF14101F); // slightly lighter than background
  static const darkOnSurface = Color(0xFFE6E1E5); // White/Off-white text
  static const darkBackground = Color(0xFF0F0A15); // Deep Violet Black
  static const darkSurfaceVariant =
      Color(0xFF1F1A2E); // Card background (Lighter Violet)
  static const darkOnSurfaceVariant =
      Color(0xFFCAC4D0); // Soft grey-purple text

  // Outline and shadow
  static const darkOutline = Color(0xFF49454F);
  static const darkShadow = Color(0xFF000000);
  static const darkInversePrimary = Color(0xFF6750A4);

  // AQI-specific colors
  static const aqiGood = Color(0xFF66BB6A);
  static const aqiModerate = Color(0xFFFFB74D);
  static const aqiUnhealthy = Color(0xFFFF7043);
  static const aqiHazardous = Color(0xFFFF2E63); // Red/Pink
}

/// Font size constants
class FontSizes {
  static const double displayLarge = 57.0;
  static const double displayMedium = 45.0;
  static const double displaySmall = 36.0;
  static const double headlineLarge = 32.0;
  static const double headlineMedium = 28.0;
  static const double headlineSmall = 24.0;
  static const double titleLarge = 22.0;
  static const double titleMedium = 16.0;
  static const double titleSmall = 14.0;
  static const double labelLarge = 14.0;
  static const double labelMedium = 12.0;
  static const double labelSmall = 11.0;
  static const double bodyLarge = 16.0;
  static const double bodyMedium = 14.0;
  static const double bodySmall = 12.0;
}

// =============================================================================
// THEMES
// =============================================================================

/// Light theme with modern, neutral aesthetic
ThemeData get lightTheme => ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.light(
        primary: LightModeColors.lightPrimary,
        onPrimary: LightModeColors.lightOnPrimary,
        primaryContainer: LightModeColors.lightPrimaryContainer,
        onPrimaryContainer: LightModeColors.lightOnPrimaryContainer,
        secondary: LightModeColors.lightSecondary,
        onSecondary: LightModeColors.lightOnSecondary,
        tertiary: LightModeColors.lightTertiary,
        onTertiary: LightModeColors.lightOnTertiary,
        error: LightModeColors.lightError,
        onError: LightModeColors.lightOnError,
        errorContainer: LightModeColors.lightErrorContainer,
        onErrorContainer: LightModeColors.lightOnErrorContainer,
        surface: LightModeColors.lightSurface,
        onSurface: LightModeColors.lightOnSurface,
        surfaceContainerHighest: LightModeColors.lightSurfaceVariant,
        onSurfaceVariant: LightModeColors.lightOnSurfaceVariant,
        outline: LightModeColors.lightOutline,
        shadow: LightModeColors.lightShadow,
        inversePrimary: LightModeColors.lightInversePrimary,
      ),
      brightness: Brightness.light,
      scaffoldBackgroundColor: LightModeColors.lightBackground,
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        foregroundColor: LightModeColors.lightOnSurface,
        elevation: 0,
        scrolledUnderElevation: 0,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(
            color: LightModeColors.lightOutline.withOpacity(0.2),
            width: 1,
          ),
        ),
      ),
      textTheme: _buildTextTheme(Brightness.light),
    );

/// Dark theme with good contrast and readability
ThemeData get darkTheme => ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.dark(
        primary: DarkModeColors.darkPrimary,
        onPrimary: DarkModeColors.darkOnPrimary,
        primaryContainer: DarkModeColors.darkPrimaryContainer,
        onPrimaryContainer: DarkModeColors.darkOnPrimaryContainer,
        secondary: DarkModeColors.darkSecondary,
        onSecondary: DarkModeColors.darkOnSecondary,
        tertiary: DarkModeColors.darkTertiary,
        onTertiary: DarkModeColors.darkOnTertiary,
        error: DarkModeColors.darkError,
        onError: DarkModeColors.darkOnError,
        errorContainer: DarkModeColors.darkErrorContainer,
        onErrorContainer: DarkModeColors.darkOnErrorContainer,
        surface: DarkModeColors.darkSurface,
        onSurface: DarkModeColors.darkOnSurface,
        surfaceContainerHighest: DarkModeColors.darkSurfaceVariant,
        onSurfaceVariant: DarkModeColors.darkOnSurfaceVariant,
        outline: DarkModeColors.darkOutline,
        shadow: DarkModeColors.darkShadow,
        inversePrimary: DarkModeColors.darkInversePrimary,
      ),
      brightness: Brightness.dark,
      scaffoldBackgroundColor: DarkModeColors.darkSurface,
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        foregroundColor: DarkModeColors.darkOnSurface,
        elevation: 0,
        scrolledUnderElevation: 0,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(
            color: DarkModeColors.darkOutline.withOpacity(0.2),
            width: 1,
          ),
        ),
      ),
      textTheme: _buildTextTheme(Brightness.dark),
    );

/// Build text theme using Inter font family
TextTheme _buildTextTheme(Brightness brightness) {
  return TextTheme(
    displayLarge: GoogleFonts.inter(
      fontSize: FontSizes.displayLarge,
      fontWeight: FontWeight.w400,
      letterSpacing: -0.25,
    ),
    displayMedium: GoogleFonts.inter(
      fontSize: FontSizes.displayMedium,
      fontWeight: FontWeight.w400,
    ),
    displaySmall: GoogleFonts.inter(
      fontSize: FontSizes.displaySmall,
      fontWeight: FontWeight.w400,
    ),
    headlineLarge: GoogleFonts.inter(
      fontSize: FontSizes.headlineLarge,
      fontWeight: FontWeight.w600,
      letterSpacing: -0.5,
    ),
    headlineMedium: GoogleFonts.inter(
      fontSize: FontSizes.headlineMedium,
      fontWeight: FontWeight.w600,
    ),
    headlineSmall: GoogleFonts.inter(
      fontSize: FontSizes.headlineSmall,
      fontWeight: FontWeight.w600,
    ),
    titleLarge: GoogleFonts.inter(
      fontSize: FontSizes.titleLarge,
      fontWeight: FontWeight.w600,
    ),
    titleMedium: GoogleFonts.inter(
      fontSize: FontSizes.titleMedium,
      fontWeight: FontWeight.w500,
    ),
    titleSmall: GoogleFonts.inter(
      fontSize: FontSizes.titleSmall,
      fontWeight: FontWeight.w500,
    ),
    labelLarge: GoogleFonts.inter(
      fontSize: FontSizes.labelLarge,
      fontWeight: FontWeight.w500,
      letterSpacing: 0.1,
    ),
    labelMedium: GoogleFonts.inter(
      fontSize: FontSizes.labelMedium,
      fontWeight: FontWeight.w500,
      letterSpacing: 0.5,
    ),
    labelSmall: GoogleFonts.inter(
      fontSize: FontSizes.labelSmall,
      fontWeight: FontWeight.w500,
      letterSpacing: 0.5,
    ),
    bodyLarge: GoogleFonts.inter(
      fontSize: FontSizes.bodyLarge,
      fontWeight: FontWeight.w400,
      letterSpacing: 0.15,
    ),
    bodyMedium: GoogleFonts.inter(
      fontSize: FontSizes.bodyMedium,
      fontWeight: FontWeight.w400,
      letterSpacing: 0.25,
    ),
    bodySmall: GoogleFonts.inter(
      fontSize: FontSizes.bodySmall,
      fontWeight: FontWeight.w400,
      letterSpacing: 0.4,
    ),
  );
}
