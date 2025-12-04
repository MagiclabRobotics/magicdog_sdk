#pragma once
#include "magic_export.h"
#include "magic_type.h"

#include <atomic>
#include <functional>
#include <memory>
#include <string>

namespace magic::dog::display {

class DisplayController;
using DisplayControllerPtr = std::unique_ptr<DisplayController>;

/**
 * @class DisplayController
 * @brief A class encapsulating display control functions, providing interfaces for display query, set, etc.
 *
 * This class is typically used to control display output in robots or smart devices, supporting face expression setting and query,
 * and providing initialization and resource release mechanisms.
 */
class MAGIC_EXPORT_API DisplayController final : public NonCopyable {
 public:
  /**
   * @brief Constructor, initializes the display controller object.
   *        Can be used to construct internal state, allocate resources, etc.
   */
  DisplayController();

  /**
   * @brief Destructor, releases display controller resources.
   *        Ensures playback is stopped and underlying resources are cleaned up.
   */
  ~DisplayController();

  /**
   * @brief Initialize the display control module.
   * @return Returns true on success, false on failure.
   */
  bool Initialize();

  /**
   * @brief Shutdown the display controller and release resources.
   *        Used together with Initialize to ensure safe exit.
   */
  void Shutdown();

  /**
   * @brief Get all face expressions.
   * @param[out] data Face expression data (returned by reference).
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status, returns Status::OK on success.
   */
  Status GetAllFaceExpressions(std::vector<FaceExpression>& data, int timeout_ms = 5000);

  /**
   * @brief Set face expression.
   * @param expression_id Face expression ID.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status, returns Status::OK on success.
   */
  Status SetFaceExpression(int expression_id, int timeout_ms = 5000);

  /**
   * @brief Get current face expression.
   * @param[out] data Current face expression (returned by reference).
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status, returns Status::OK on success.
   */
  Status GetFaceExpression(FaceExpression& data, int timeout_ms = 5000);

 private:
  std::atomic_bool is_shutdown_{true};  // Flag indicating whether initialized
};

}  // namespace magic::dog::display