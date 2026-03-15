#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/float64.hpp>
#include <std_msgs/msg/float32_multi_array.hpp>
#include <mutex>

#include "dhdc.h"
#include <cmath>

using std::placeholders::_1;

class HapticDriver : public rclcpp::Node
{
public:
    // Constructor function
    HapticDriver(): Node("haptic_driver")
    {   
        // Ros Args
        this->declare_parameter("use_haptic", false);
        this->get_parameter("use_haptic", use_haptic_); 
        
        // Publishers
        position_pub_ = this->create_publisher<std_msgs::msg::Float32MultiArray>("/haptic_position", 10);
        orientation_pub_ = this->create_publisher<std_msgs::msg::Float32MultiArray>("/haptic_orientation", 10);
        ft_pub_ = this->create_publisher<std_msgs::msg::Float32MultiArray>("/haptic_rendering_force", 10);
        button_pub_ = this->create_publisher<std_msgs::msg::Bool>("/haptic_button", 10);
        

        // Subscriber
        ft_sub_ = this->create_subscription<std_msgs::msg::Float32MultiArray>("/ft_data_processed", 10, std::bind(&HapticDriver::ft_callback, this, _1));

        // Initialize device
        if (!init_device())
        {
            RCLCPP_ERROR(this->get_logger(), "Failed to initialize Omega7");
            rclcpp::shutdown();
        }

        // 1 kHz publish timer and 4 kHz render timer 
        publish_timer_ = this->create_wall_timer(std::chrono::milliseconds(1),std::bind(&HapticDriver::update_loop, this));
        render_timer_ = this->create_wall_timer(std::chrono::microseconds(250),std::bind(&HapticDriver::render_loop, this));
    }

    ~HapticDriver()
    {
        dhdClose();
    }

private:
    bool use_haptic_;
    std::mutex ft_mutex_;
    double ft_force_[3] = {0.0, 0.0, 0.0};

    // Publishers
    rclcpp::Publisher<std_msgs::msg::Float32MultiArray>::SharedPtr position_pub_;
    rclcpp::Publisher<std_msgs::msg::Float32MultiArray>::SharedPtr orientation_pub_;
    rclcpp::Publisher<std_msgs::msg::Float32MultiArray>::SharedPtr ft_pub_;
    rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr button_pub_;
    
    // Subscriber
    rclcpp::Subscription<std_msgs::msg::Float32MultiArray>::SharedPtr ft_sub_;
    
    // Timer
    rclcpp::TimerBase::SharedPtr render_timer_;
    rclcpp::TimerBase::SharedPtr publish_timer_;

    bool init_device()
    {
        if (dhdGetDeviceCount() <= 0)
        {
            RCLCPP_ERROR(this->get_logger(), "No haptic device found.");
            return false;
        }

        if (dhdOpen() < 0)
        {
            RCLCPP_ERROR(this->get_logger(), "Cannot open device.");
            return false;
        }

        dhdEnableForce(DHD_ON);
        dhdEmulateButton(DHD_ON);

        return true;
    }

    void ft_callback(const std_msgs::msg::Float32MultiArray::SharedPtr msg)
    {   
        if (!use_haptic_) return;
        
        if (msg->data.size() < 3) 
        {
            RCLCPP_WARN(this->get_logger(), "Received less than 3 elements, skipping");
            return;
        }

        std::lock_guard<std::mutex> lock(ft_mutex_);

        ft_force_[0] = msg->data[0];
        ft_force_[1] = msg->data[1];
        ft_force_[2] = msg->data[2]; 
    }

    void update_loop()
    {
        double px, py, pz;
        double roll, pitch, yaw;

        if (dhdGetPosition(&px, &py, &pz) < 0) return;
        if (dhdGetOrientationRad(&roll, &pitch, &yaw) < 0) return;

        // Publish pose
        std_msgs::msg::Float32MultiArray position_msg;
        std_msgs::msg::Float32MultiArray orientation_msg;

        position_msg.data.push_back(px);
        position_msg.data.push_back(py);
        position_msg.data.push_back(pz);

        orientation_msg.data.push_back(roll);
        orientation_msg.data.push_back(pitch);
        orientation_msg.data.push_back(yaw);

        position_pub_->publish(position_msg);
        orientation_pub_->publish(orientation_msg);

        // Publish rendering force
        std_msgs::msg::Float32MultiArray ft_msg;
        ft_msg.data.push_back(ft_force_[1]);
        ft_msg.data.push_back(ft_force_[0]);
        ft_msg.data.push_back(-0.5*ft_force_[2]);

        ft_pub_->publish(ft_msg);

        // Publish button
        std_msgs::msg::Bool button_msg;  

        int button_state = dhdGetButton(0);
        if (button_state < 0)
            return;
        button_msg.data = (button_state != 0);

        button_pub_->publish(button_msg);
    }

    void render_loop()
    {
    if (use_haptic_)
    {   
        // Here robot sensor x is haptic y axis and sensor y is haptic x axis
        std::lock_guard<std::mutex> lock(ft_mutex_);
        dhdSetForceAndTorqueAndGripperForce(ft_force_[1], ft_force_[0], -ft_force_[2],0.0, 0.0, 0.0, 0.0);
    }
    else
    {
        dhdSetForceAndTorqueAndGripperForce(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
    }
    }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<HapticDriver>());
    rclcpp::shutdown();
    return 0;
}